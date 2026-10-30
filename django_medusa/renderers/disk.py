import mimetypes
import os

from django.conf import settings

from .base import COMMON_MIME_MAPS, BaseStaticSiteRenderer, get_test_client

__all__ = ('DiskStaticSiteRenderer', )


# Unfortunately split out from the class at the moment to allow rendering with
# several processes via `multiprocessing`.
# TODO: re-implement within the class if possible?
def _disk_render_path(args):
    client, path, view = args
    if not client:
        client = get_test_client()
    if path:
        DEPLOY_DIR = settings.MEDUSA_DEPLOY_DIR
        realpath = path
        if path.startswith("/"):
            realpath = realpath[1:]

        needs_ext = path.endswith("/")

        output_dir = os.path.abspath(os.path.join(
            DEPLOY_DIR,
            os.path.dirname(realpath)
        ))
        os.makedirs(output_dir, exist_ok=True)
        outpath = os.path.join(DEPLOY_DIR, realpath)

        resp = client.get(path)
        if resp.status_code != 200:
            raise Exception(
                "Rendering '%s' returned HTTP status %s"
                % (path, resp.status_code)
            )
        if needs_ext:
            mime = resp['Content-Type']
            mime = mime.split(';', 1)[0]

            # Check our override list above first.
            ext = COMMON_MIME_MAPS.get(
                mime,
                mimetypes.guess_extension(mime)
            )
            if ext:
                outpath += "index" + ext
            else:
                # Default to ".html"
                outpath += "index.html"
        print(outpath)
        with open(outpath, 'wb') as f:
            f.write(resp.content)


class DiskStaticSiteRenderer(BaseStaticSiteRenderer):

    def render_path(self, path=None, view=None):
        _disk_render_path((self.client, path, view))

    def generate(self):
        if getattr(settings, "MEDUSA_MULTITHREAD", False):
            from multiprocessing import (
                Pool, cpu_count, get_all_start_methods, get_context,
            )

            print("Generating with up to %d processes..." % cpu_count())
            # Workers render through the Django test client, so they must
            # inherit the parent's configured Django state. Python 3.14
            # stopped defaulting to "fork", so request it explicitly and
            # fall back to the platform default where it is unavailable
            # (e.g. Windows, where MEDUSA_MULTITHREAD is best-effort).
            if 'fork' in get_all_start_methods():
                pool = get_context('fork').Pool(cpu_count())
            else:
                pool = Pool(cpu_count())
            with pool:
                # pool.map raises here if any worker failed, so rendering
                # errors propagate to the management command instead of
                # being silently dropped.
                pool.map(
                    _disk_render_path,
                    ((None, path, None) for path in self.paths),
                    chunksize=5
                )
        else:
            # Use standard, serial upload.
            self.client = get_test_client()
            for path in self.paths:
                self.render_path(path=path)
