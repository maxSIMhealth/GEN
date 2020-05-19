from django import template

from forums.models import Comment, Discussion

register = template.Library()


@register.simple_tag
def checkvotes_discussion(user_id, pk):
    discussion = Discussion.objects.get(pk=pk)
    if discussion.votes.exists(user_id):
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
