from django.apps import AppConfig
from celery.schedules import crontab


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        from myproject.celery import app as celery_app

        celery_app.conf.beat_schedule = {
            "process-mobile-orders": {
                "task": "orders.tasks.process_mobile_orders",
                "schedule": 30.0,  # Run every 30 seconds
            },
        }
        return super().ready()
