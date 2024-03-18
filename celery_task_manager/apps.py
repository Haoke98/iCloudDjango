from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CeleryTaskManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'celery_task_manager'
    verbose_name = _('Task Management')
