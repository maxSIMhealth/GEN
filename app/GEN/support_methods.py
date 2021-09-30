def enrollment_test():
    """
    Empty test, just to pass request data into course_enrollment_check decorator.
    """
    return True


def duplicate_name(item):
    item.name += " (Copy)"
    return item


def duplicate_item(item, callback=None):
    """
    Based on: https://stackoverflow.com/a/52761222/2066218

    Duplicate a model instance, making copies of all foreign keys pointing to it.
    There are 3 steps that need to occur in order:

    1.  Enumerate the related child objects and m2m relations, saving in lists/dicts
    2.  Copy the parent object per django docs (doesn't copy relations)
    3a. Copy the child objects, relating to the copied parent object
    3b. Re-create the m2m relations on the copied parent object

    The optional callback function is called once the item has been duplicated but before
    it's saved. The new object is passed its only argument and it should return the object to be save.
    It can be used e.g. to update the name of the duplicated object

    ```
    def duplicate_name(object):
        object.name += ' (Copy)'
        return object

    duplicate(object, callback=duplicate_name)
    ```
    """
    related_objects_to_copy = []
    relations_to_set = {}

    # Iterate through all the fields in the parent object looking for related fields
    fields = item._meta.get_fields()
    for field in fields:
        if field.one_to_many:
            # One to many fields are backward relationships where many child
            # objects are related to the parent. Enumerate them and save a list
            # so we can copy them after duplicating our parent object.
            print(f"Found a one-to-many field: {field.name}")

            # 'field' is a ManyToOneRel which is not iterable, we need to get
            # the object attribute itself.
            related_object_manager = getattr(item, field.get_accessor_name())
            related_objects = list(related_object_manager.all())
            if related_objects:
                print(f" - {len(related_objects)} related objects to copy")
                related_objects_to_copy += related_objects

        elif field.one_to_one:
            if hasattr(item, field.name):
                # In testing, these relationships are not being copied automatically.
                print(f"Found a one-to-one field: {field.name}")
                related_object = getattr(item, field.name)
                related_objects_to_copy.append(related_object)

        elif field.many_to_one:
            # In testing, these relationships are preserved when the parent
            # object is copied, so they don't need to be copied separately.
            print(f"Found a many-to-one field: {field.name}")

        elif field.many_to_many and not hasattr(field, "field"):
            # Many to many fields are relationships where many parent objects
            # can be related to many child objects. Because of this the child
            # objects don't need to be copied when we copy the parent, we just
            # need to re-create the relationship to them on the copied parent.
            related_object_manager = getattr(item, field.name)

            if related_object_manager.through:
                # Many to many relations with a through table are handled as many to one relationships
                # between the object and the through table so we can skip this
                continue

            print(f"Found a many-to-many field: {field.name}")
            relations = list(related_object_manager.all())
            if relations:
                print(f" - {len(relations)} relations to set")
                relations_to_set[field.name] = relations

    # Duplicate the parent object
    # https://docs.djangoproject.com/en/3.0/topics/db/queries/#copying-model-instances
    item.pk = None
    item.id = None

    if callback and callable(callback):
        item = callback(item)

    item.save()
    print(f"Copied parent object ({str(item)})")

    # Copy the one-to-many child objects and relate them to the copied parent
    for related_object in related_objects_to_copy:
        # Iterate through the fields in the related object to find the one that
        # relates to the parent model.
        for related_object_field in related_object._meta.fields:
            if related_object_field.related_model == item.__class__ or (
                    hasattr(related_object_field.related_model, "_meta")
                    and related_object_field.related_model._meta.proxy_for_model
                    == item.__class__
            ):
                # If the related_model on this field matches the parent
                # object's class, perform the copy of the child object and set
                # this field to the parent object, creating the new
                # child -> parent relationship.
                setattr(related_object, related_object_field.name, item)
                new_related_object = duplicate_item(related_object)
                new_related_object.save()

                text = str(related_object)
                text = (text[:40] + "..") if len(text) > 40 else text
                print(f"|- Copied child object ({text})")

    # Set the many-to-many relations on the copied parent
    for field_name, relations in relations_to_set.items():
        # Get the field by name and set the relations, creating the new
        # relationships.
        field = getattr(item, field_name)
        field.set(relations)
        text_relations = []
        for relation in relations:
            text_relations.append(str(relation))
        print(
            f"|- Set {len(relations)} many-to-many relations on {field_name} {text_relations}"
        )

    return item
