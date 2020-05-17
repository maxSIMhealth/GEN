from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course, User
from .forms import UploadVideoForm
from .models import VideoFile


@login_required
def list_videos(request, pk):
    course = get_object_or_404(Course, pk=pk)
    forums = course.forums.all()
    user = request.user

    # filter videos submitted by instructors
    course_instructors = course.instructors.all()
    course_videos = course.videos.filter(author__in=course_instructors)

    # gets the videos submitted by the user
    user_videos = user.videos.get_queryset().filter(course=course)

    # checks if the current user is a course instructor
    if course in user.instructor.all():
        # returns all participants videos to the instructor (excluding his own)
        participants_videos = course.videos.exclude(author=user)
    else:
        participants_videos = ""
    #     # returns only videos submitted by current user
    #     user_videos = user.videos.get_queryset()

    # TODO: old code, check if it should be deleted
    # media_list = []
    # for forum in forums:
    #     if forum.media.kind == 'YTB':
    #         media_list.append(forum)

    return render(
        request,
        "list_videos.html",
        {
            "course": course,
            "forums": forums,
            "course_videos": course_videos,
            "user_videos": user_videos,
            "participants_videos": participants_videos,
        },
    )


@login_required
def upload_video(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # FIXME: the forums object will probably have to be removed later on
    forums = course.forums.all()

    if request.method == "POST":
        form = UploadVideoForm(request.POST, request.FILES)

        if "Cancel" in request.POST["submit"]:
            return redirect("list_videos", pk=course.pk)
        if "submit" in request.POST and form.is_valid():
            video = VideoFile.objects.create(
                title=form.cleaned_data.get("title"),
                description=form.cleaned_data.get("description"),
                author=request.user,
                course=course,
                file=form.files.get("file"),
            )
            # TODO: this forum code is functional but will not be used for now
            # forum = Forum.objects.create(
            #     course=course,
            #     name=form.cleaned_data.get('title'),
            #     description=form.cleaned_data.get('description'),
            #     video=video,
            #     author=request.user
            # )
            video.save()
            video.generate_video_thumbnail()
            # forum.save()
            return redirect("list_videos", pk=course.pk)
    else:
        form = UploadVideoForm()

    return render(
        request, "upload_video.html", {"form": form, "course": course, "forums": forums}
    )


@login_required
def delete_video(request, pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    video = get_object_or_404(VideoFile, pk=video_pk)
    user = get_object_or_404(User, pk=request.user.pk)

    if video.author == user:
        if request.method == "POST":
            if "confirm" in request.POST:
                video.delete()
                return redirect("list_videos", pk=course.pk)
        else:
            return render(
                request,
                "delete_video_confirmation.html",
                {"course": course, "video": video},
            )
    else:
        return render(request, "permission_error.html")


@login_required
def video_player(request, pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    video = get_object_or_404(VideoFile, pk=video_pk)

    return render(request, "video_player.html", {"course": course, "video": video})


# @login_required
# def video_comments(request, pk, video_pk):
#     course = get_object_or_404(Course, pk=pk)
#     forums = course.forums.all()
#     video = get_object_or_404(VideoFile, pk=video_pk)
#     forum = forums.filter(name=video.title)[0]
#     gamification = course.enable_gamification

#     if request.method == 'POST':
#         form = NewCommentForm(request.POST)
#         if form.is_valid():
#             forum.last_updated = timezone.now()
#             forum.save()
#             comment = Comment.objects.create(
#                 message=form.cleaned_data.get('message'),
#                 forum=forum,
#                 author=request.user
#             )
#             comment.save()
#             my_kwargs = dict(
#                 pk=course.pk,
#                 video_pk=video.pk
#             )
#             return redirect('video_comments', **my_kwargs)
#     else:
#         form = NewCommentForm()

#     return render(request, 'video_comments.html',
#                   {'forum': forum,
#                    'course': course,
#                    'video': video,
#                    'form': form,
#                    'gamification': gamification})
