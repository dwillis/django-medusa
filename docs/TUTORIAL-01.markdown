# Tutorial 1: The "hello world" of Django static websites

Requires Python 3.12+ and Django 6.1.

## Preliminaries

Set up a virtualenv, install Django and django-medusa, create a Django project
for this little website-ish thing:

    python -m venv my_medusa
    cd my_medusa
    source bin/activate

    pip install "django>=6.1,<6.2"
    pip install "https://github.com/mtigas/django-medusa/tarball/master#egg=django-medusa"

    django-admin startproject my_medusa_site
    cd my_medusa_site

## Configure your `settings.py`

In your favorite text editor, open `my_medusa_site/settings.py`.

Add the following to `INSTALLED_APPS`:

    'django_medusa',
    'my_medusa_site',

And then add this stuff to settings, too, preferably near the bottom of
the file:

    # django_medusa -- disk-based renderer
    import os
    MEDUSA_RENDERER_CLASS = "django_medusa.renderers.DiskStaticSiteRenderer"
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    MEDUSA_DEPLOY_DIR = os.path.join(
        PROJECT_DIR, '..', "_output"
    )

## Create a view and a URL

Modern Django projects start with no default page, so create one. Make
`my_medusa_site/views.py` contain:

    from django.http import HttpResponse

    def home(request):
        return HttpResponse(
            "<html><body><h1>Hello, static world!</h1></body></html>"
        )

Then wire it up in `my_medusa_site/urls.py`:

    from django.urls import path
    from . import views

    urlpatterns = [
        path('', views.home),
    ]

## Create your renderer

Create a `my_medusa_site/renderers.py` file (i.e., place `renderers.py` in the
directory alongside `settings.py` and `urls.py`), and make it contain:

    from django_medusa.renderers import StaticSiteRenderer

    class HomeRenderer(StaticSiteRenderer):
        def get_paths(self):
            return frozenset([
                "/",
            ])

    renderers = [HomeRenderer, ]

## Build you a static, Django-generated website

Now run the following (assuming you are in the same directory as `manage.py`)

    python manage.py staticsitegen

You should now see an `_output` directory show up next to your `manage.py`.
Inside it, you'll find an `index.html` file containing the "Hello, static
world!" page from your view.

Congratulations, you've just rendered a Django website (sort of) to a static
website.

## Preview it like a static host would

The `_output` directory is a complete static site. To preview it the same
way a static host (e.g. GitHub Pages) would serve it:

    python -m http.server --directory _output 8000

Then open http://localhost:8000/ in your browser. See the README for how to
publish this output to GitHub Pages with GitHub Actions.

For more advanced topics (dynamically generating `renderer.get_paths` based
on models, collecting static assets, publishing, etc), see [the
README][readme] and stay tuned for future tutorials.

[readme]: ../README.markdown
