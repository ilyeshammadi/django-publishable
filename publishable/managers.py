from django.db import models

from .constants import TYPES
from .context_managers import DraftController


def select(instance):
    draft_controller = DraftController(instance=instance)
    return draft_controller.select()


def select_from_queryset(queryset):
    if not DraftController.is_draft:
        return queryset.filter(type=TYPES.PUBLISHED)
    return queryset.filter(type=TYPES.DRAFT, is_deleted=False)


class PublishableManager(models.Manager):

    def get(self, *args, **kwargs):
        return select(super(PublishableManager, self).get(*args, **kwargs))

    def first(self):
        return select(super(PublishableManager, self).first())

    def last(self):
        return select(super(PublishableManager, self).last())

    def filter(self, *args, **kwargs):
        return select_from_queryset(super(PublishableManager, self).filter(*args, **kwargs))

    def all(self):
        return select_from_queryset(super(PublishableManager, self).all())

    def _all(self):
        return super(PublishableManager, self).get_queryset()
