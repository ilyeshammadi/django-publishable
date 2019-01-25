from django.db import models

from .constants import TYPES


def clone_model(original_model):
    """
    Create a copy of a Django mode
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
            # Select the through model
            through = field.remote_field.through

            # Get the name of the field
            for f in through._meta.get_fields():
                if isinstance(f, models.ForeignKey):
                    m = f.rel.to
                    if isinstance(original_model, m):
                        parent_model_field_name = f.attname

            formated_parent_model_field_name = '_'.join(parent_model_field_name.split('_')[:2])

            filter_params = {
                parent_model_field_name: original_model.pk,
            }
            all_link_models = through.objects.filter(**filter_params)

            for link_model in all_link_models:
                link_model.pk = None
                setattr(link_model, formated_parent_model_field_name, destination_model)
                try:
                    link_model.save(broadcast_draft=False)
                except:
                    link_model.save()


    destination_model.save(broadcast_draft=False)
    return destination_model
