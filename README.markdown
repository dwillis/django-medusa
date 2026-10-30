# django-medusa

[![Tests](https://github.com/dwillis/django-medusa/actions/workflows/test.yml/badge.svg)](https://github.com/dwillis/django-medusa/actions/workflows/test.yml)

A super simple "static site generator" for Django sites. [Read more about this project here](https://mike.tig.as/blog/2012/06/30/django-medusa-rendering-django-sites-static-html/).

© 2011-2014 Mike Tigas. Licensed under the [MIT License](LICENSE).

---

**Note**: This fork is modernized for Python 3.12+ and Django 6.1 as of
v0.4.0 (disk renderer; the S3 and App Engine backends are deprecated).
The original project, [mtigas/django-medusa](https://github.com/mtigas/django-medusa),
has been unmaintained since 2014. If you want to use something similar,
look at the following which are still somewhat active, as of January 2016:

* [django-bakery](https://github.com/datadesk/django-bakery), built and maintained
  the lovely people at the [Los Angeles Times Data Desk](http://datadesk.latimes.com/).
  (Read about it [here](http://datadesk.latimes.com/posts/2012/03/introducing-django-bakery/).)
* [The alsoicode/django-medusa fork](https://github.com/alsoicode/django-medusa), by [Brandon Taylor](https://github.com/alsoicode). Among other things, it's been kept up to date for newer versions of Django.
* [django-freeze](https://github.com/fabiocaccamo/django-freeze) by [Fabio Caccamo](https://github.com/fabiocaccamo).
* [django-staticgen](https://github.com/mishbahr/django-staticgen) by [Mishbah Razzaque](https://github.com/mishbahr).

---

**django-medusa** allows rendering a Django-powered website into a static website a la *Jekyll*,
*Movable Type*, or other static page generation CMSes or frameworks.
It is designed to be as simple as possible and allow the
easy(ish) conversion of existing dynamic Django-powered websites -- nearly any
existing Django site installation (not relying on highly-dynamic content) can
be converted into a static generator which mirror's that site's output.

Given a "renderer" that defines a set of URLs (see below), this uses Django's
built-in `TestClient` to render out those views to static files on disk,
ready to be served by any static host (e.g. GitHub Pages, Netlify, or an
`aws s3 sync` upload).

At the moment, this likely does not scale to extremely large websites due to
the use of the internal `TestClient`. But django-medusa optionally uses the
`multiprocessing` library to speed up the rendering process by rendering many
views in parallel.

**For those uninterested in the nitty-gritty**, there are tutorials/examples
in the `docs` dir:

* [Tutorial 1: Hello World](docs/TUTORIAL-01.markdown)

## Requirements

* Python 3.12, 3.13, or 3.14
* Django 6.1
* The disk-based renderer (`DiskStaticSiteRenderer`) is the supported backend.
  The S3 and App Engine backends are deprecated and retained only for import
  compatibility.

## Renderer classes

Renderers live in `renderers.py` in each `INSTALLED_APP`.

Simply subclassing the `StaticSiteRenderer` class and defining `get_paths`
works:

    from django_medusa.renderers import StaticSiteRenderer

    class HomeRenderer(StaticSiteRenderer):
        def get_paths(self):
            return frozenset([
                "/",
                "/about/",
                "/sitemap.xml",
            ])

    renderers = [HomeRenderer, ]

A more complex example:

    from django_medusa.renderers import StaticSiteRenderer
    from myproject.blog.models import BlogPost


    class BlogPostsRenderer(StaticSiteRenderer):
        def get_paths(self):
            paths = ["/blog/", ]

            items = BlogPost.objects.filter(is_live=True).order_by('-pubdate')
            for item in items:
                paths.append(item.get_absolute_url())

            return paths

    renderers = [BlogPostsRenderer, ]

Or even:

    from django_medusa.renderers import StaticSiteRenderer
    from myproject.blog.models import BlogPost
    from django.urls import reverse


    class BlogPostsRenderer(StaticSiteRenderer):
        def get_paths(self):
            # A "set" so we can throw items in blindly and be guaranteed that
            # we don't end up with dupes.
            paths = set(["/blog/", ])

            items = BlogPost.objects.filter(is_live=True).order_by('-pubdate')
            for item in items:
                # BlogPost detail view
                paths.add(item.get_absolute_url())

                # The generic date-based list views.
                paths.add(reverse('blog:archive_day', args=(
                    item.pubdate.year, item.pubdate.month, item.pubdate.day
                )))
                paths.add(reverse('blog:archive_month', args=(
                    item.pubdate.year, item.pubdate.month
                )))
                paths.add(reverse('blog:archive_year', args=(item.pubdate.year,)))

            # Cast back to a list since that's what we're expecting.
            return list(paths)

    renderers = [BlogPostsRenderer, ]

## Renderer backends

### Disk-based static site renderer

Example settings:

    INSTALLED_APPS = (
        # ...
        # ...
        'django_medusa',
    )
    # ...
    MEDUSA_RENDERER_CLASS = "django_medusa.renderers.DiskStaticSiteRenderer"
    MEDUSA_MULTITHREAD = True
    MEDUSA_DEPLOY_DIR = os.path.abspath(os.path.join(
        REPO_DIR,
        'var',
        "html"
    ))

### S3-based site renderer

**Deprecated:** this backend targets the legacy `boto` SDK (not `boto3`) and is
retained only for import compatibility. Prefer rendering to disk and syncing
the output with a supported AWS tool.

Example settings:

    INSTALLED_APPS = (
        # ...
        # ...
        'django_medusa',
    )
    # ...
    MEDUSA_RENDERER_CLASS = "django_medusa.renderers.S3StaticSiteRenderer"
    MEDUSA_MULTITHREAD = True
    AWS_ACCESS_KEY = ""
    AWS_SECRET_ACCESS_KEY = ""
    MEDUSA_AWS_STORAGE_BUCKET_NAME = "" # (also accepts AWS_STORAGE_BUCKET_NAME)

Be aware that the S3 renderer will overwrite any existing files that match
URL paths in your site.

The S3 backend will force "index.html" to be the Default Root Object for each
directory, so that "/about/" would actually be uploaded as "/about/index.html",
but properly loaded by the browser at the "/about/" URL.

**BONUS:** Additionally, the S3 renderer keeps the "Content-Type" HTTP header
that the view returns: if "/foo/json/" returns a JSON file (application/json),
the file will be uploaded to "/foo/json/index.html" but will be served as
application/json in the browser -- and will be accessible from "/foo/json/".

### App Engine-based site renderer

**Deprecated:** this backend targets the legacy (Python 2) App Engine SDK and
is retained only for import compatibility. Prefer rendering to disk and
deploying the output yourself.

Example settings:

    INSTALLED_APPS = (
        # ...
        # ...
        'django_medusa',
    )
    # ...
    MEDUSA_RENDERER_CLASS = "django_medusa.renderers.GAEStaticSiteRenderer"
    MEDUSA_MULTITHREAD = True
    MEDUSA_DEPLOY_DIR = os.path.abspath(os.path.join(
        REPO_DIR,
        'var',
        "html"
    ))
    GAE_APP_ID = ""

This generates a `app.yaml` file and a `deploy` directory in your
`MEDUSA_DEPLOY_DIR`. The `app.yaml` file contains the URL mappings to upload
the entire site as a static files.

App Engine generally follows filename extensions as the mimetype. If you have
paths that don't have an extension and are *not* HTML files (i.e.
"/foo/json/", "/feeds/blog/", etc.), the mimetype from the "Content-Type" HTTP
header will be manually defined for this URL in the `app.yaml` path.

## Usage

1. Install `django-medusa` from this repository and add `django_medusa`
   to `INSTALLED_APPS`:

       pip install git+https://github.com/dwillis/django-medusa.git@v0.4.0
2. Select a renderer backend (supported: disk) in your settings.
3. Create renderer classes in `renderers.py` under the apps you want to render.
4. `django-admin staticsitegen` (or `python manage.py staticsitegen`)
5. ???
6. Profit!

#### Example

From the first example in the "**Renderer classes**" section, using the
disk-based backend.

    $ django-admin staticsitegen
    Found renderers for 'myproject'...
    Skipping app 'django.contrib.syndication'... (No 'renderers.py')
    Skipping app 'django.contrib.sitemaps'... (No 'renderers.py')
    Skipping app 'typogrify'... (No 'renderers.py')

    Generating with up to 8 processes...
    /project_dir/var/html/index.html
    /project_dir/var/html/about/index.html
    /project_dir/var/html/sitemap.xml

## Local preview and publishing to GitHub Pages

The disk renderer mirrors your URL structure to files (`/about/` becomes
`about/index.html`), so the output is directly servable by any static host,
including GitHub Pages.

1. Build into a clean output directory:
   `python manage.py staticsitegen`
2. Collect static assets into the same directory by setting `STATIC_URL` to
   `'/static/'` and `STATIC_ROOT` to a `static` subdirectory of
   `MEDUSA_DEPLOY_DIR`, then run `python manage.py collectstatic --noinput`.
3. Preview the result exactly as it will be served:
   `python -m http.server --directory path/to/output 8000`
4. Deploy with GitHub Actions. In the **site's** repository, set the Pages
   source to "GitHub Actions" and add a workflow like:

       name: Publish
       on: [push, workflow_dispatch]
       permissions:
         contents: read
         pages: write
         id-token: write
       jobs:
         build:
           runs-on: ubuntu-latest
           steps:
             - uses: actions/checkout@v4
             - uses: actions/setup-python@v5
               with:
                 python-version: '3.12'
             - run: pip install -r requirements.txt
             - run: python manage.py staticsitegen
             - run: python manage.py collectstatic --noinput
             - uses: actions/upload-pages-artifact@v3
               with:
                 path: path/to/output
         deploy:
           needs: build
           runs-on: ubuntu-latest
           environment:
             name: github-pages
             url: ${{ steps.deployment.outputs.page_url }}
           steps:
             - id: deployment
               uses: actions/deploy-pages@v4

Things to be aware of:

* Django views, models, and forms run at **build time** only; the published
  site is static files. Anything per-request (auth, server-side forms,
  search) will not work after publishing.
* For a user/organization site (`USER.github.io`) or a custom domain,
  root-relative URLs work as-is. For a project site
  (`USER.github.io/REPOSITORY/`), prefix your URLs with the repository name.
* Give non-HTML output explicit file extensions. GitHub Pages picks the
  `Content-Type` from the file extension, not from the response headers your
  views returned at build time.
* Add a `404.html` to your renderer paths if you want a custom error page.
