# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .constants import TYPES, PublishingStatus
from .managers import PublishableManager
from .utils import clone_model


class Draft(models.Model):
    """
    Model that will contain a draft model
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.CharField(max_length=255, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def publish(self):
        self.content_object.publish()

    def __str__(self):
        return 'Draft ({0}: pk={1}'.format(self.content_type, self.object_id)


PUBLISHING_STATUS_CHOICES = (
    (PublishingStatus.DRAFT, PublishingStatus.DRAFT),
    (PublishingStatus.PUBLISHED, PublishingStatus.PUBLISHED),
    (PublishingStatus.PUBLISHING, PublishingStatus.PUBLISHING),
    (PublishingStatus.ERROR, PublishingStatus.ERROR),
)


class Publisher(models.Model):
    class Meta:
        abstract = True

    drafts = models.ManyToManyField(Draft)

    publishing_status = models.CharField(max_length=255, choices=PUBLISHING_STATUS_CHOICES,
                                         default=PublishingStatus.DRAFT)

    def add_draft(self, draft):
        # Change the status to DRAFT
        self.publishing_status = PublishingStatus.DRAFT
        self.save()

        self.drafts.add(draft)

    def publish_drafts(self):
        """
        Publish all the drafts in a specific Publisher
        Run this function in an async job like a celery task
        """
        try:
            # Change the status to PUBLISHING
            self.publishing_status = PublishingStatus.PUBLISHING
            self.save()

            # Publish all drafts
            for draft in self.drafts.all():
                draft.publish()

            # Delete all drafts
            for draft in self.drafts.all():
                draft.delete()

            # Change the status to PUBLISHED
            self.publishing_status = PublishingStatus.PUBLISHED
            self.save()
        except Exception as e:
            # Change the status to ERROR
            self.publishing_status = PublishingStatus.ERROR
            self.save()
            raise e


TYPES_CHOICES = (
    (TYPES.DRAFT, TYPES.DRAFT),
    (TYPES.PUBLISHED, TYPES.PUBLISHED)
)


class Publishable(models.Model):
    class Meta:
        abstract = True

    type = models.CharField(max_length=255, choices=TYPES_CHOICES, default=TYPES.DRAFT)
    published = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="published_instance")

    is_deleted = models.BooleanField(default=False)

    objects = PublishableManager()

    def publish(self):
        if not self.is_deleted:
            # Create a copy of the wanted to publish instance
            published = clone_model(self)

            previous_published_id = self.published.id if self.published else None
            self.published = published
            self.save(broadcast_draft=False)

            if previous_published_id:
                self.__class__.objects._all().get(pk=previous_published_id).delete(fake=False)
        else:
            if self.published:
                self.published.delete(fake=False)
            self.delete(fake=False)

    def delete(self, using=None, keep_parents=False, fake=True):
        if self.type == TYPES.DRAFT:
            if not fake:
                return super(Publishable, self).delete(using, keep_parents)
            self.is_deleted = True
            self.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, broadcast_draft=True):
        super(Publishable, self).save(force_insert, force_update, using, update_fields)
        if broadcast_draft:
            self.broadcast_need_to_published()

    def broadcast_need_to_published(self):
        """
        Broadcast the returned draft to the publisher
        this function needs to extended in order to publish on a
        specific publisher
        :return: Draft
        """
        return (
            Draft.objects.get(object_id=self.id)
            if Draft.objects.filter(object_id=self.id).exists()
            else Draft.objects.create(content_object=self)
        )
