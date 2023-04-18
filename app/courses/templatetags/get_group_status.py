from courses.models import Status

from django import template

register = template.Library()


@register.simple_tag
def get_group_status(user, group):
    if group is not None:
        try:
            group_status = Status.objects.get(learner=user, group=group)
        except Status.DoesNotExist:
            group_status = None
    else:
        group_status = None

    return group_status
