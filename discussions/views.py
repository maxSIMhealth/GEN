from urllib.parse import urlparse

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# from django.core.files import File
# from django.core.files.storage import FileSystemStorage
# from django.core.files.images import ImageFile
# from django.views.generic import ListView

from courses.models import Course, Section
from .forms import NewCommentForm, NewDiscussionForm
from .models import Comment, Discussion
from .support_methods import discussion_enable_check

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
def discussion_comments(request, pk, section_pk, discussion_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    discussion = get_object_or_404(Discussion, pk=discussion_pk)
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
                        pk=course.pk, section_pk=section.pk, discussion_pk=discussion.pk
                    )
                    return redirect("discussion_comments", **my_kwargs)
            else:
                form = NewCommentForm()

            return render(
                request,
                "comments.html",
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
            raise Http404("You do not fulfill the requirements to access this page.")
    else:
        raise Http404("Discussion board does not exist.")


@login_required
def new_discussion(request, pk, section_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    discussion = Discussion.objects.all()

    if request.method == "POST":
        form = NewDiscussionForm(course, request.POST)
        if "Cancel" in request.POST["submit"]:
            pass
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
        "new_discussion.html",
        {"discussion": discussion, "course": course, "section": section, "form": form,},
    )


@login_required
def upvote_discussion(request, pk, section_pk, discussion_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    discussion = Discussion.objects.get(pk=discussion_pk)
    discussion.votes.up(request.user.id)

    # checking if the user is voting from the discussions list or from discussion itself
    path = urlparse(request.META["HTTP_REFERER"]).path + "upvote"

    my_kwargs = dict(pk=course.pk, section_pk=section.pk, discussion_pk=discussion.pk)

    if request.path == path:
        return redirect("discussion_comments", **my_kwargs)
    else:
        return redirect("section", pk=course.pk, section_pk=section.pk)


@login_required
def clearvote_discussion(request, pk, section_pk, discussion_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    discussion = Discussion.objects.get(pk=discussion_pk)
    discussion.votes.delete(request.user.id)

    # checking if the user is voting from the discussions list or from discussion itself
    path = urlparse(request.META["HTTP_REFERER"]).path + "clearvote"

    my_kwargs = dict(pk=course.pk, section_pk=section.pk, discussion_pk=discussion.pk)

    if request.path == path:
        return redirect("discussion_comments", **my_kwargs)
    else:
        return redirect("section", pk=course.pk, section_pk=section.pk)


@login_required
def upvote_comment(request, pk, section_pk, discussion_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.votes.up(request.user.id)

    my_kwargs = dict(pk=pk, section_pk=section_pk, discussion_pk=discussion_pk)

    return redirect("discussion_comments", **my_kwargs)


@login_required
def clearvote_comment(request, pk, section_pk, discussion_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.votes.delete(request.user.id)

    my_kwargs = dict(pk=pk, section_pk=section_pk, discussion_pk=discussion_pk)

    return redirect("discussion_comments", **my_kwargs)
