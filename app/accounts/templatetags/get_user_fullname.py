from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_user_fullname(context):
    user = context["user"]

    if user.id is None:
        fullname = None
    else:
        fullname = f"{user.first_name} {user.last_name}"

    return fullname
