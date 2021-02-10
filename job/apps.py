from django.apps import AppConfig


class JobConfig(AppConfig):
    name = 'job'

    def ready(self):
        import job.views
