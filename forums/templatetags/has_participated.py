from django import template
from forums.models import Forum

register = template.Library()


@register.filter(name="has_participated")
def has_participated(user, discussion_name):
    discussion = Forum.objects.get(name=discussion_name)
    did_user_comment = discussion.comments.filter(author=user).exists()

    return did_user_comment
