from django import template

register = template.Library()


@register.filter(name="has_participated")
def has_participated(user, discussion):
    did_user_comment = discussion.comments.filter(author=user).exists()

    return did_user_comment
