from django_medusa.renderers import StaticSiteRenderer


class SiteRenderer(StaticSiteRenderer):
    def get_paths(self):
        return [
            "/",
            "/about/",
            "/data.json",
            "/feed/",
            "/binary/",
        ]


renderers = [SiteRenderer]
