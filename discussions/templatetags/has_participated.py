from django import template

from discussions.support_methods import has_participated

register = template.Library()


@register.filter(name="has_participated")
def did_user_comment(user, discussion):
    return has_participated(user, discussion)
