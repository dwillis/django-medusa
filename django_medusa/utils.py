import importlib
import importlib.util

from django.apps import apps
from django.conf import settings


def get_static_renderers():
    module_name = 'renderers'
    renderers = []

    modules_to_check = []

    # Hackish: do this in case we have some project top-level
    # (homepage, etc) urls defined project-level instead of app-level.
    settings_module = settings.SETTINGS_MODULE
    if settings_module:
        if "." in settings_module:
            # strip off '.settings" from end of module
            # (want project module, if possible)
            settings_module = settings_module.split(".", 1)[0]
        modules_to_check.append(settings_module)

    # INSTALLED_APPS via the app registry (handles AppConfig entries),
    # ignoring the project itself and this django_medusa module.
    modules_to_check += [
        app_config.name
        for app_config in apps.get_app_configs()
        if app_config.name not in ("django_medusa", settings_module)
    ]

    for app in dict.fromkeys(modules_to_check):
        try:
            module = importlib.import_module(app)
        except ImportError:
            print("Skipping app '%s'... (Not found)" % app)
            continue
        if getattr(module, '__path__', None) is None:
            print("Skipping app '%s'... (Not a package)" % app)
            continue
        if importlib.util.find_spec('%s.%s' % (app, module_name)) is None:
            print("Skipping app '%s'... (No 'renderers.py')" % app)
            continue
        # Any error raised while importing an existing renderers module
        # propagates to the caller rather than being silently skipped.
        app_render_module = importlib.import_module('%s.%s' % (app, module_name))
        app_renderers = getattr(app_render_module, 'renderers', None)
        if app_renderers is None:
            print("Skipping app '%s'... ('%s.renderers' does not contain "
                  "'renderers' var (list of render classes)" % (app, app))
            continue
        renderers += app_renderers
        print("Found renderers for '%s'..." % app)
    return tuple(renderers)
