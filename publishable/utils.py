from django.db import models

from .constants import TYPES


def clone_model(original_model):
    """
    Create a compay of a Django mode
    :param original_model: models.Model
    :return: models.Model
    """
    # Create a local copy of the model to avoid references errors
    model = original_model.__class__.objects._all().get(pk=original_model.id)

    # This block of codes forces Django to clone to model and the simple fields
    # CharField, TextField etc...
    destination_model = model
    destination_model.pk = None
    destination_model.type = TYPES.PUBLISHED
    destination_model.save(broadcast_draft=False)

    # Search for the ManyToManyField and copy it's content into the model
    all_model_fields = original_model._meta.get_fields()
    for field in all_model_fields:
        if isinstance(field, models.ManyToManyField):
            # Get the name of the M2M field
            field_attrname = field.attname

            # Get a reference to the M2M
            field_content = getattr(original_model, field_attrname)

            # Select the field in the destination model
            destination_field_content = getattr(destination_model, field_attrname)

            # Copy all the items in the M2M to the destination model
            destination_field_content.add(*field_content.all())

    destination_model.save(broadcast_draft=False)
    return destination_model
