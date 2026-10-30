import io
from contextlib import redirect_stdout

from django.test import SimpleTestCase, override_settings

from django_medusa.utils import get_static_renderers
from tests.renderers import SiteRenderer
from tests.testapp.renderers import AppRenderer


class DiscoveryTests(SimpleTestCase):

    def collect(self):
        out = io.StringIO()
        with redirect_stdout(out):
            renderers = get_static_renderers()
        return renderers, out.getvalue()

    def test_discovers_project_and_app_renderers(self):
        renderers, output = self.collect()
        self.assertIn(SiteRenderer, renderers)
        self.assertIn(AppRenderer, renderers)
        self.assertIn("Found renderers for 'tests'...", output)
        self.assertIn("Found renderers for 'tests.testapp'...", output)

    def test_appconfig_entries_are_resolved(self):
        with override_settings(
            INSTALLED_APPS=['django_medusa',
                            'tests.testapp.apps.TestAppConfig']
        ):
            renderers, output = self.collect()
        self.assertIn(AppRenderer, renderers)

    def test_apps_without_renderers_are_skipped(self):
        with override_settings(
            INSTALLED_APPS=['django_medusa', 'django.contrib.contenttypes']
        ):
            renderers, output = self.collect()
        self.assertNotIn(AppRenderer, renderers)
        self.assertIn(
            "Skipping app 'django.contrib.contenttypes'... "
            "(No 'renderers.py')", output
        )

    def test_errors_inside_renderers_module_propagate(self):
        with override_settings(
            INSTALLED_APPS=['django_medusa', 'tests.brokenapp']
        ):
            with redirect_stdout(io.StringIO()):
                with self.assertRaises(RuntimeError):
                    get_static_renderers()
