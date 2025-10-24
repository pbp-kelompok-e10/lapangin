from django.apps import AppConfig

class ReviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.review' # Or modules.review, etc.

    def ready(self):
        import modules.review.signals
