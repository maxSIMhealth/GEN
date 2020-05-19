from django import template

# from forums.models import Forum
from forums.support_methods import discussion_enable_check, has_user_voted

register = template.Library()


class DiscussionDetails:
    def __init__(self, enabled, voted):
        self.enabled = enabled
        self.voted = voted


@register.simple_tag
def discussion_details_get(user, discussion):
    enabled = discussion_enable_check(user, discussion)
    voted = has_user_voted(user, discussion)

    return DiscussionDetails(enabled, voted)
