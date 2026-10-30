import glob
import json
import os
import shutil
import tempfile

from django.test import SimpleTestCase, override_settings

from django_medusa.renderers import StaticSiteRenderer
from tests.renderers import SiteRenderer


class FailingRenderer(StaticSiteRenderer):
    def get_paths(self):
        return ["/fails/"]


class DiskRendererTests(SimpleTestCase):

    def setUp(self):
        self.deploy_dir = tempfile.mkdtemp(prefix='medusa-test-')
        self.addCleanup(shutil.rmtree, self.deploy_dir, True)

    def generate(self, renderer_class, multithread=False):
        with override_settings(MEDUSA_DEPLOY_DIR=self.deploy_dir,
                               MEDUSA_MULTITHREAD=multithread):
            renderer_class().generate()

    def assert_generated_output(self):
        def read(*parts, mode='rb'):
            with open(os.path.join(self.deploy_dir, *parts), mode) as f:
                return f.read()

        self.assertEqual(read('index.html'), b"<html><body>Home</body></html>")
        self.assertEqual(
            read('about', 'index.html'),
            b"<html><body>About</body></html>"
        )
        self.assertEqual(json.loads(read('data.json')), {"ok": True})
        self.assertEqual(json.loads(read('feed', 'index.json')),
                         {"items": []})
        binary_files = glob.glob(
            os.path.join(self.deploy_dir, 'binary', 'index.*')
        )
        self.assertEqual(len(binary_files), 1)
        with open(binary_files[0], 'rb') as f:
            self.assertEqual(f.read(), b"\x00\x01\x02\x03")

    def test_serial_generation(self):
        self.generate(SiteRenderer)
        self.assert_generated_output()

    def test_multiprocess_generation(self):
        self.generate(SiteRenderer, multithread=True)
        self.assert_generated_output()

    def test_non_200_response_raises_serially(self):
        with self.assertRaises(Exception):
            self.generate(FailingRenderer)

    def test_non_200_response_raises_from_worker_pool(self):
        with self.assertRaises(Exception):
            self.generate(FailingRenderer, multithread=True)


class TestClientHelperTests(SimpleTestCase):

    def test_testserver_host_is_whitelisted(self):
        from django.conf import settings

        from django_medusa.renderers.base import get_test_client

        with override_settings(ALLOWED_HOSTS=[]):
            client = get_test_client()
            self.assertIn('testserver', settings.ALLOWED_HOSTS)
            response = client.get('/')
        self.assertEqual(response.status_code, 200)
