import uuid

from courses.models import ADMINS, EDITORS, INSTRUCTORS, LEARNERS, PUBLIC

from django.db.models import Q


def allow_access(user, course, item):
    """
    Verifies if the user has permission to access a specific item.
    """

    access_restriction = item.access_restriction
    access_override = item.author_access_override

    if access_override and item.author == user:
        access_allowed = True
    else:
        if access_restriction == PUBLIC and user in course.members.all():
            access_allowed = True
        elif access_restriction == LEARNERS and user in course.learners.all():
            access_allowed = True
        elif access_restriction == INSTRUCTORS and user in course.instructors.all():
            access_allowed = True
        elif access_restriction == EDITORS and user in course.editors.all():
            access_allowed = True
        elif access_restriction == ADMINS and user.is_staff:
            access_allowed = True
        elif user.is_staff:
            access_allowed = True
        else:
            access_allowed = False

    return access_allowed


def check_is_editor(course_object, user):
    is_editor = bool(course_object in user.editor.all())

    return is_editor


def check_is_instructor(course_object, user):
    is_instructor = bool(course_object in user.instructor.all())

    return is_instructor


def filter_by_access_restriction(course_object, items, user):
    # check if user is a course instructor or editor
    is_instructor = check_is_instructor(course_object, user)
    is_editor = check_is_editor(course_object, user)

    # show all sections if the user is a course instructor, superuser, or staff
    if user.is_superuser or user.is_staff:
        items_filtered = items.all()
    elif is_editor and is_instructor:
        items_filtered = items.filter(
            Q(access_restriction=INSTRUCTORS)
            | Q(access_restriction=EDITORS)
            | Q(access_restriction=PUBLIC)
        )
    elif is_editor:
        items_filtered = items.filter(
            Q(access_restriction=EDITORS) | Q(access_restriction=PUBLIC)
        )
    elif is_instructor:
        items_filtered = items.filter(
            Q(access_restriction=PUBLIC) | Q(access_restriction=INSTRUCTORS)
        )
    else:
        items_filtered = items.filter(
            (Q(access_restriction=PUBLIC) | Q(access_restriction=LEARNERS))
            & Q(published=True)
        )
        items_override = items.filter(Q(author_access_override=True) & Q(author=user))
        items_filtered = items_filtered | items_override

    return items_filtered


def course_sections_list(course_object, user):
    sections = course_object.sections.all()
    filtered_sections = filter_by_access_restriction(course_object, sections, user)

    return filtered_sections


def user_directory_path(instance, filename, randomize_filename: bool = True):
    ext = filename.split(".")[-1]
    if randomize_filename:
        random_filename = str(uuid.uuid4().hex)
        filename = "%s.%s" % (random_filename, ext)
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.author.id, filename)


def user_directory_path_not_random(instance, filename):
    return user_directory_path(instance, filename, randomize_filename=False)
