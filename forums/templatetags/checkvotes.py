from django import template
from forums.models import Forum, Comment

register = template.Library()


@register.simple_tag
def checkvotes_forum(user_id, pk):
    forum = Forum.objects.get(pk=pk)
    if forum.votes.exists(user_id):
        return True
    else:
        return False


@register.simple_tag
def checkvotes_comment(user_id, pk):
    comment = Comment.objects.get(pk=pk)
    if comment.votes.exists(user_id):
        return True
    else:
        return False
