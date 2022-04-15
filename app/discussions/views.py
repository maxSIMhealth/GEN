from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from GEN.decorators import course_enrollment_check, check_permission
from GEN.support_methods import enrollment_test

# from django.core.files import File
# from django.core.files.storage import FileSystemStorage
# from django.core.files.images import ImageFile
# from django.views.generic import ListView

from courses.models import Course, Section
from .forms import NewCommentForm, NewDiscussionForm
from .models import Comment, Discussion
from .support_methods import discussion_enable_check, has_participated

# @login_required
# def list_pdfs(request, pk):
#     course = get_object_or_404(Course, pk=pk)
#     discussions = course.discussions.all()
#     media_list = []

#     for discussion in discussions:
#         if discussion.media.kind == 'PDF':
#             media_list.append(discussion)

#     return render(request, 'list_pdfs.html',
#                   {'course': course, 'discussions': discussions, 'media_list': media_list})


# class DiscussionListView(ListView):
# https://ccbv.co.uk/projects/Django/2.1/django.views.generic.list/ListView/
# Render some list of objects, set by `self.model` or `self.queryset`.
# `self.queryset` can actually be any iterable of items, not just a queryset.
# model = Discussion
# context_object_name = 'discussions'
# template_name = 'home.html'


@login_required
@course_enrollment_check(enrollment_test)
@check_permission("discussion")
def discussion_comments(request, pk, section_pk, sectionitem_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    discussion = get_object_or_404(Discussion, pk=sectionitem_pk)
    video = discussion.video
    gamification = course.enable_gamification

    if discussion.published:

        # check if discussion has a requirement and if it should be enabled
        discussion_enabled = discussion_enable_check(request.user, discussion)

        if discussion_enabled:

            if request.method == "POST":
                form = NewCommentForm(request.POST)
                if form.is_valid():
                    discussion.last_updated = timezone.now()
                    discussion.save()
                    comment = Comment.objects.create(
                        message=form.cleaned_data.get("message"),
                        discussion=discussion,
                        author=request.user,
                    )
                    comment.save()
                    my_kwargs = dict(
                        pk=course.pk, section_pk=section.pk, sectionitem_pk=discussion.pk
                    )

                    update_discussion_section_status(request, section)

                    return redirect("discussion_comments", **my_kwargs)
            else:
                form = NewCommentForm()

            return render(
                request,
                "discussions/comments.html",
                {
                    "discussion": discussion,
                    "course": course,
                    "section": section,
                    "video": video,
                    "form": form,
                    "gamification": gamification,
                },
            )
        else:
            messages.error(
                request, _("You do not fulfill the requirements to access this page.")
            )
            return redirect("section", pk=course.pk, section_pk=section.pk)
    else:
        messages.error(request, _("Discussion board does not exist."))
        return redirect("section", pk=course.pk, section_pk=section.pk)


def update_discussion_section_status(request, section):
    section_status = section.status.filter(learner=request.user).get()
    if not section_status.completed:
        section_discussions = Discussion.objects.filter(section=section)
        section_discussions_participated = []
        for discussion in section_discussions:
            section_discussions_participated.append(has_participated(request.user, discussion))
        if all(section_discussions_participated):
            # section_status = section.status.filter(learner=request.user).get()
            section_status.completed = True
            section_status.save()


@login_required
@course_enrollment_check(enrollment_test)
def new_discussion(request, pk, section_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    discussion = Discussion.objects.all()

    if request.method == "POST":
        form = NewDiscussionForm(course, request.POST)
        # if "Cancel" in request.POST["submit"]:
        #     pass
        if "submit" in request.POST and form.is_valid():
            discussion = Discussion.objects.create(
                course=course,
                section=section,
                published=True,
                name=form.cleaned_data.get("name"),
                description=form.cleaned_data.get("description"),
                video=form.cleaned_data.get("video"),
                author=request.user,
            )
            discussion.save()

        messages.success(request, _("Discussion board created."))
        return redirect("section", pk=course.pk, section_pk=section.pk)
        # media_form = NewMediaForm(request.POST)
        # if form.is_valid() and media_form.is_valid():
        #     media = MediaFile.objects.create(
        #         title=media_form.cleaned_data.get('title'),
        #         kind=media_form.cleaned_data.get('kind'),
        #         author=request.user,
        #         url=media_form.cleaned_data.get('url'),
        #     )
        #     discussion = Discussion.objects.create(
        #         course=course,
        #         name=form.cleaned_data.get('name'),
        #         description=form.cleaned_data.get('description'),
        #         media=media,
        #         author=request.user
        #     )
        #     media.save()
        #     discussion.save()
        #     return redirect('course_discussions', pk=course.pk)
    else:
        form = NewDiscussionForm(course)
        # media_form = NewMediaForm()

    return render(
        request,
        "discussions/new_discussion.html",
        {"discussion": discussion, "course": course, "section": section, "form": form,},
    )


def update_discussion_vote(request, sectionitem_pk, remove_vote:bool=False, add_vote:bool=False):
    discussion = Discussion.objects.get(pk=sectionitem_pk)

    # checking if the user is voting from the discussions list or from discussion itself
    referer_path = request.META.get('HTTP_REFERER', None)
    if referer_path is None:
        # block requests without referer
        # raise BadRequest(_("Invalid request."))
        raise PermissionDenied()

    referer_resolve = resolve(urlparse(referer_path)[2])

    # block vote if the current user is the author
    if discussion.author == request.user:
        messages.error(request, _("You cannot vote on your own submissions."))
    else:
        if remove_vote:
            discussion.votes.delete(request.user.id)
        if add_vote:
            discussion.votes.up(request.user.id)

    return redirect(reverse(referer_resolve.view_name, kwargs=referer_resolve.kwargs))


@login_required
@course_enrollment_check(enrollment_test)
def add_discussion_vote(request, pk, section_pk, sectionitem_pk):
    return update_discussion_vote(request, sectionitem_pk, add_vote=True)


@login_required
@course_enrollment_check(enrollment_test)
def remove_discussion_vote(request, pk, section_pk, sectionitem_pk):
    return update_discussion_vote(request, sectionitem_pk, remove_vote=True)


def update_comment_vote(request, pk, section_pk, sectionitem_pk, comment_pk, remove_vote:bool=False, add_vote:bool=False):
    comment = get_object_or_404(Comment, pk=comment_pk)
    my_kwargs = dict(pk=pk, section_pk=section_pk, sectionitem_pk=sectionitem_pk)

    # block vote if the current user is the author
    if comment.author == request.user:
        messages.error(request, _("You cannot vote on your own submissions."))
    else:
        if remove_vote:
            comment.votes.delete(request.user.id)
        if add_vote:
            comment.votes.up(request.user.id)

    return redirect("discussion_comments", **my_kwargs)


@login_required
@course_enrollment_check(enrollment_test)
def add_comment_vote(request, pk, section_pk, sectionitem_pk, comment_pk):
    return update_comment_vote(request, pk, section_pk, sectionitem_pk, comment_pk, add_vote=True)


@login_required
@course_enrollment_check(enrollment_test)
def remove_comment_vote(request, pk, section_pk, sectionitem_pk, comment_pk):
    return update_comment_vote(request, pk, section_pk, sectionitem_pk, comment_pk, remove_vote=True)
