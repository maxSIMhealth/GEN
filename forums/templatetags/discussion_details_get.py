from django import template

from forums.models import Forum

register = template.Library()


class DiscussionDetails:
    def __init__(self, enabled):
        self.enabled = enabled


def discussion_enable_check(user, discussion):
    """
    Check if discussion should still be enabled for the user to participate in
    """
    requirement_fulfilled = False
    discussion_enable = False

    # check if discussion has a requirement
    if discussion.requirement:
        # check if the user has any comments on the required discussion
        did_user_comment = discussion.requirement.comments.filter(author=user).exists()

        # check if discussion requirement has been fulfilled
        requirement_fulfilled = did_user_comment

    else:
        requirement_fulfilled = True

    # check if discussion should be still available
    # TODO: this could be used in the future to also implement
    # discussion end date check
    if requirement_fulfilled:
        discussion_enable = True

    return discussion_enable


@register.simple_tag
def discussion_details_get(user, discussion):
    enabled = discussion_enable_check(user, discussion)

    return DiscussionDetails(enabled)
