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


def has_user_voted(user, discussion):
    return bool(discussion.votes.exists(user.pk))


def has_participated(user, discussion):
    did_user_comment = discussion.comments.filter(author=user).exists()

    return did_user_comment
