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

# WIP: refactoring `upload_video` method into a class-based view `UploadVideoView`.
# Decorators `block_instructor_access` and `check_if_submission_is_allowd` are related to it.
#
# def block_instructor_access(view_func):
#     def wrapper(request, *args, **kwargs):
#         user = request.user
#         course = Course.objects.get(pk=kwargs["pk"])
#         section = Section.objects.get(pk=kwargs["section_pk"])
#         is_instructor = bool(course in user.instructor.all())
#         if is_instructor:
#             messages.error(
#                 request,
#                 "Only learners are allowed to upload in this section.",
#             )
#             return HttpResponseRedirect(
#                 reverse("section", args=[course.pk, section.pk]))
#         else:
#             return view_func(request, *args, **kwargs)
#     return wrapper
#
# def check_if_submission_is_allowed(view_func):
#     def wrapper(request, *args, **kwargs):
#         request.allow_submission = False
#         # check if section type is upload
#         if request.section.section_type == "U":
#             section_items = request.section.section_items.filter(author=request.user)
#             if not section_items:
#                 request.allow_submission = True
#         elif request.section.section_type == "V":
#             if request.is_instructor:
#                 request.allow_submission = True
#         else:
#             messages.error(
#                 request,
#                 "This section does not support uploads.",
#             )
#             return HttpResponseRedirect(
#                 reverse("section", args=[request.course.pk, request.section.pk]))
#     return wrapper
