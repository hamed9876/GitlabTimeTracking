from django.apps import apps
from drf_spectacular.openapi import AutoSchema


class AppTaggedAutoSchema(AutoSchema):
    """Group endpoints in Swagger by the Django app the view belongs to."""

    def get_tags(self):
        app_label = self.view.__class__.__module__.split(".")[0]
        try:
            return [str(apps.get_app_config(app_label).verbose_name)]
        except LookupError:
            return super().get_tags()
