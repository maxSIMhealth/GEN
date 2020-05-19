from django import template

from forums.models import Discussion

register = template.Library()


@register.filter(name="has_participated")
def has_participated(user, discussion_name):
    discussion = Discussion.objects.get(name=discussion_name)
    did_user_comment = discussion.comments.filter(author=user).exists()

    return did_user_comment
