# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import model_ngettext, unquote
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from .conf import settings
from .models import LogEntry, Page
from .staticgen_pool import staticgen_pool
from .tasks import publish_pending, publish_pages, sync_pages, publish_changed

staticgen_pool.autodiscover()  # Piggyback off admin.autodiscover() to discover Staticgen views


class PageAdmin(admin.ModelAdmin):
    list_display = ('path', 'publisher_state', 'updated_at', )
    actions = ('make_dirty', )
    readonly_fields = ('publisher_state', 'updated_at', )
    search_fields = ('path', )
    object_history_template = 'admin/staticgen/page/object_history.html'
    publish_history_template = 'admin/staticgen/page/publish_history.html'
    logentry_limit = 100

    fieldsets = (
        (None, {
            'fields': ('path', 'publisher_state', 'updated_at', )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.site_id = settings.SITE_ID
        super(PageAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super(PageAdmin, self).get_queryset(request)
        queryset = queryset.on_site()
        return queryset

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_add_permission(self, request):
        return True  # pragma: no cover

    def get_urls(self):
        urls = super(PageAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = patterns(
            '',
            url(r'^publish-history/$', admin.site.admin_view(self.publish_history_view),
                name='%s_%s_publish_history' % info),
            url(r'^publish/$', admin.site.admin_view(self.publisher_view),
                name='%s_%s_publisher' % info),
        )
        return urlpatterns + urls

    def make_dirty(self, request, queryset):
        rows_updated = queryset.filter(publisher_state=self.model.PUBLISHER_STATE_PUBLISHED) \
            .update(publisher_state=self.model.PUBLISHER_STATE_CHANGED)

        message = _('{count} {verbose_name} marked as changed.').format(
            count=rows_updated, verbose_name=model_ngettext(self.opts, rows_updated)
        )
        self.message_user(request, message, messages.SUCCESS)
    make_dirty.short_description = _('Mark selected %(verbose_name_plural)s as changed')

    def get_actions(self, request):
        actions = super(PageAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def history_view(self, request, page_id, extra_context=None):
        """Overriding history_view() to use custom LogEntry model."""

        model = self.model
        obj = self.get_object(request, unquote(page_id))
        if obj is None:
            raise Http404(_('{name} with primary key {pk} does not exist.').format(
                name=force_text(model._meta.verbose_name),
                pk=escape(page_id)
            ))

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        # Then get the history for this object.
        action_list = LogEntry.objects.filter(
            page_id=unquote(page_id),
        ).select_related().order_by('-action_time')[:self.logentry_limit]

        opts = model._meta
        context = dict(
            title=_('History: %s') % force_text(obj),
            action_list=action_list,
            module_name=capfirst(force_text(opts.verbose_name_plural)),
            object=obj,
            opts=opts,
            preserved_filters=self.get_preserved_filters(request),
        )
        context.update(extra_context or {})
        request.current_app = self.admin_site.name
        return TemplateResponse(request, self.object_history_template, context)

    def publish_history_view(self, request, extra_context=None):
        action_list = LogEntry.objects.filter(
            site_id=settings.SITE_ID,
            page__isnull=True
        ).select_related().order_by('-action_time')[:self.logentry_limit]

        opts = self.model._meta
        context = dict(
            title=_('Publish History'),
            action_list=action_list,
            module_name=capfirst(force_text(opts.verbose_name_plural)),
            opts=opts,
            preserved_filters=self.get_preserved_filters(request),
        )
        context.update(extra_context or {})
        request.current_app = self.admin_site.name
        return TemplateResponse(request, self.publish_history_template, context)

    def publisher_view(self, request, extra_context=None):
        action = request.GET.get('action', None)
        if action not in ('sync', 'pending', 'changed', 'all', ):
            return HttpResponseBadRequest()

        if action == 'sync':
            sync_pages.delay()
        elif action == 'pending':
            publish_pending.delay()
        elif action == 'changed':
            publish_changed.delay()
        elif action == 'all':
            publish_pages.delay()

        opts = self.model._meta
        preserved_filters = self.get_preserved_filters(request)
        msg = _('Your request is processing in the background. '
                'Please check the "Publish History" for updates.')
        self.message_user(request, msg, messages.SUCCESS)

        if self.has_change_permission(request, None):
            redirect_url = reverse('admin:%s_%s_changelist' % (opts.app_label, opts.model_name),
                                   current_app=self.admin_site.name)
        else:  # pragma: no cover
            redirect_url = reverse('admin:index', current_app=self.admin_site.name)

        redirect_url = add_preserved_filters(
            {'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
        return HttpResponseRedirect(redirect_url)


admin.site.register(Page, PageAdmin)
