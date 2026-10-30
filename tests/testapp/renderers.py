from django_medusa.renderers import StaticSiteRenderer


class AppRenderer(StaticSiteRenderer):
    def get_paths(self):
        return ["/about/"]


renderers = [AppRenderer]
