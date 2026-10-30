import os
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'django-medusa-tests'
DEBUG = True
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
USE_TZ = True

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django_medusa',
    'tests',
    'tests.testapp',
]

ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

MEDUSA_RENDERER_CLASS = 'django_medusa.renderers.DiskStaticSiteRenderer'
MEDUSA_DEPLOY_DIR = os.path.join(
    tempfile.gettempdir(), 'django_medusa_test_output'
)
MEDUSA_MULTITHREAD = False
