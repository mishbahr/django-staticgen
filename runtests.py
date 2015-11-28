import sys

try:
    from django.conf import settings

    settings.configure(
        DEBUG=True,
        LANGUAGE_CODE='en-us',
        USE_TZ=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'staticgen',
            }
        },
        ROOT_URLCONF='example.urls',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.sessions',
            'django.contrib.admin',
            'django.contrib.sitemaps',
            'staticgen',
            'example',  # used for testing
        ],
        SITE_ID=1,
        NOSE_ARGS=['-s'],
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.SHA1PasswordHasher',
        ),
        DEFAULT_FILE_STORAGE='staticgen.storage.S3DefaultStorage',
        STATICFILES_STORAGE='staticgen.storage.S3StaticStorage',
        AWS_S3_DEFAULTFILES_LOCATION='media',
        AWS_S3_STATICFILES_LOCATION='static',
        AWS_ACCESS_KEY_ID='AKIAIOSFODNN7EXAMPLE',
        AWS_SECRET_ACCESS_KEY='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        AWS_STORAGE_BUCKET_NAME='staticgen-bucket',
        AWS_S3_CUSTOM_DOMAIN='staticgen-bucket.s3.amazonaws.com',
        MEDIA_ROOT='/media/',
        STATIC_ROOT='/static/',
        STATIC_URL='https://staticgen-bucket.s3.amazonaws.com/static/',
        MEDIA_URL='https://staticgen-bucket.s3.amazonaws.com/media/',
        CELERY_ALWAYS_EAGER=True,
        STATICGEN_MULTITHREAD=False,
    )

    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()

    from django_nose import NoseTestSuiteRunner
except ImportError:
    import traceback
    traceback.print_exc()
    raise ImportError('To fix this error, run: pip install -r requirements-test.txt')


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    test_runner = NoseTestSuiteRunner(verbosity=1)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
