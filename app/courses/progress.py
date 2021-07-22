def progress(user, course, items):
    from core.support_methods import allow_access

    items = items.filter(published = True)
    items_total = 0
    items_participation = 0

    for item in items:
        if item._meta.model_name != "section":
            access_allowed = allow_access(user, course, item)
        else:
            access_allowed = True

        if access_allowed == True:
            items_total += 1
            if item._meta.model_name == "discussion":
                if item.comments.filter(author=user).exists():
                    items_participation += 1
            if item._meta.model_name == "quiz":
                if item.quizscore_set.filter(student=user).exists():
                    items_participation += 1
            if item._meta.model_name == "section":
                if item.status.filter(learner=user, completed=True).exists():
                    items_participation += 1

    items_progress = {"max": items_total, "current": items_participation}

    return items_progress
