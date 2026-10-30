import io
import os
import shutil
import tempfile
from contextlib import redirect_stdout

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


class StaticSiteGenCommandTests(SimpleTestCase):

    def test_command_generates_site(self):
        deploy_dir = tempfile.mkdtemp(prefix='medusa-cmd-test-')
        self.addCleanup(shutil.rmtree, deploy_dir, True)

        out = io.StringIO()
        with override_settings(MEDUSA_DEPLOY_DIR=deploy_dir,
                               MEDUSA_MULTITHREAD=False):
            # Renderer discovery reports progress with plain print().
            with redirect_stdout(out):
                call_command('staticsitegen')

        self.assertTrue(os.path.exists(os.path.join(deploy_dir,
                                                    'index.html')))
        self.assertTrue(os.path.exists(os.path.join(deploy_dir, 'about',
                                                    'index.html')))
        self.assertTrue(os.path.exists(os.path.join(deploy_dir,
                                                    'data.json')))
        output = out.getvalue()
        self.assertIn("Found renderers for 'tests'...", output)
