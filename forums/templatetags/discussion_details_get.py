from django import template
from forums.support_methods import discussion_enable_check, has_user_voted

register = template.Library()


class DiscussionDetails:
    __slots__ = "enabled", "voted"
    # def __init__(self, enabled, voted):
    #     self.enabled = enabled
    #     self.voted = voted


@register.simple_tag
def discussion_details_get(user, discussion):
    discussion_details = DiscussionDetails()
    discussion_details.enabled = discussion_enable_check(user, discussion)
    discussion_details.voted = has_user_voted(user, discussion)

    return discussion_details
