from django import template
from forums.models import Forum, Comment

register = template.Library()

@register.simple_tag
def countvotes(user_id, kind):
  if kind == "forum":
    items = Forum.objects.filter(author = user_id)
  elif kind == "comment":
    items = Comment.objects.filter(author = user_id)

  score = 0

  for item in items:
    score += item.votes.count()

  return score