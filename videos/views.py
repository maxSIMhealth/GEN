from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course, Section, User
from discussions.models import Discussion
from .forms import UploadVideoForm
from .models import VideoFile


@login_required
def upload_video(request, pk, section_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)

    # check if user is a course instructor
    is_instructor = bool(course in request.user.instructor.all())

    # check if section type is upload
    if section.section_type == "U" or section.section_type == "V":

        if request.method == "POST":
            form = UploadVideoForm(request.POST, request.FILES)

            if "Cancel" in request.POST["submit"]:
                return redirect("section", pk=course.pk, section_pk=section.pk)
            if "submit" in request.POST and form.is_valid():
                video = VideoFile.objects.create(
                    name=form.cleaned_data.get("name"),
                    description=form.cleaned_data.get("description"),
                    author=request.user,
                    course=course,
                    file=form.files.get("file"),
                    section=section,
                    # if instructor, the video gets published
                    published=is_instructor,
                )
                video.save()
                video.generate_video_thumbnail()
                return redirect("section", pk=course.pk, section_pk=section.pk)
        else:
            form = UploadVideoForm()

        return render(
            request,
            "upload_video.html",
            {"form": form, "course": course, "section": section},
        )
    else:
        raise Http404("This section does not support uploads.")


@login_required
def publish_video(request, pk, section_pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    video = get_object_or_404(VideoFile, pk=video_pk)
    user = get_object_or_404(User, pk=request.user.pk)

    if video.author == user:
        if request.method == "POST":
            if "confirm" in request.POST:
                # if section has parameter 'create_discussion' enabled, create
                # a discussion using the video's parameters and put it on the
                # 'section_output'
                if section.create_discussions:
                    discussion = Discussion.objects.create(
                        course=course,
                        section=section.section_output,
                        published=True,
                        name=video.name,
                        description=video.description,
                        video=video,
                        author=request.user,
                    )
                    discussion.save()

                video.published = True
                video.save()
                return redirect("section", pk=course.pk, section_pk=section.pk)
        else:
            return render(
                request,
                "publish_video_confirmation.html",
                {"course": course, "section": section, "video": video},
            )
    else:
        return render(request, "permission_error.html")


@login_required
def delete_video(request, pk, section_pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    video = get_object_or_404(VideoFile, pk=video_pk)
    user = get_object_or_404(User, pk=request.user.pk)

    # check if user is a course instructor
    is_instructor = bool(course in request.user.instructor.all())

    if video.author == user:
        # instructor should be able to delete published videos
        if is_instructor or (not video.published):
            if request.method == "POST":
                if "confirm" in request.POST:
                    video.delete()
                    return redirect("section", pk=course.pk, section_pk=section.pk)
            else:
                return render(
                    request,
                    "delete_video_confirmation.html",
                    {"course": course, "section": section, "video": video},
                )
        else:
            return render(request, "permission_error.html")
    else:
        return render(request, "permission_error.html")


@login_required
def video_player(request, pk, section_pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    video = get_object_or_404(VideoFile, pk=video_pk)

    return render(
        request,
        "video_player.html",
        {"course": course, "section": section, "video": video},
    )
