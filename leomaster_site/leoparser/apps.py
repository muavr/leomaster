from django.apps import AppConfig


class LeoparserConfig(AppConfig):
    name = 'leoparser'

    def ready(self):
        import leoparser.signals
