from django.apps import AppConfig


class ProjectConfig(AppConfig):
    name = "project"

    def ready(self):
        # To avoid putting the signals code in the __init__.py file or
        # models.py file, we import the signals module here.
        pass
