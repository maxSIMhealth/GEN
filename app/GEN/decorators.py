from functools import wraps

from courses.models import Course, Section
from courses.support_methods import requirement_fulfilled

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def course_enrollment_check(test_func):
    """
    Checks if the user is enrolled in the requested course.
    Code based on the native 'user_passes_test' django decorator.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            pk = kwargs["pk"]
            course_object = get_object_or_404(Course, pk=pk)
            user = request.user

            if user not in course_object.members.all():
                raise PermissionDenied("Access denied. User not enrolled in course.")
            else:
                return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def check_permission(item_type):
    """
    Checks if the user is allowed to access the requested item.

        Parameters:
            item_type (str): SectionItem type (game, contentitem, discussion, quiz, videofile)

    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from core.support_methods import allow_access
            from courses.models import Section, SectionItem

            course_pk = kwargs["pk"]
            course_obj = get_object_or_404(Course, pk=course_pk)
            if item_type == "section":
                item_pk = kwargs["section_pk"]
                item_obj = get_object_or_404(Section, pk=item_pk)
            else:
                item_pk = kwargs["sectionitem_pk"]
                item_obj = get_object_or_404(SectionItem, pk=item_pk)

            user = request.user

            access_allowed = allow_access(user, course_obj, item_obj)

            if access_allowed:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("Access denied.")

        return _wrapped_view

    return decorator


def check_requirement():
    """
    Checks if the user has fulfilled the request item requirements.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if "section_pk" in kwargs:
                section_pk = kwargs["section_pk"]
                item = get_object_or_404(Section, pk=section_pk)
            else:
                course_pk = kwargs["pk"]
                item = get_object_or_404(Course, pk=course_pk)

            fulfilled = requirement_fulfilled(user, item)

            if fulfilled:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied(
                    "You have not fulfilled the requirement to access the requested item."
                )

        return _wrapped_view

    return decorator


# def subject_test(f, subject):
#     def test_user_for_subject(request, subject, *args, **kwargs):
#         if not UserSubject.objects.filter(user=request.user, subject=subject).exists():
#             retun HttpResponseForbidden('Access denied!')
#         else:
#             return f(request, *args, **kwargs)
#     return test_user_for_subject
