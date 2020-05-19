from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from courses.models import Course, Section, User
from .forms import UploadVideoForm
from .models import VideoFile


@login_required
def upload_video(request, pk, section_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)

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
                    published=True,
                )
                video.save()
                video.generate_video_thumbnail()
                return redirect("section", pk=course.pk, section_pk=section.pk)
        else:
            form = UploadVideoForm()

        return render(
            request,
            "upload_video.html",
            {"form": form, "course": course, "current_section": section},
        )
    else:
        raise Http404("This section does not support uploads.")


@login_required
def delete_video(request, pk, section_pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    video = get_object_or_404(VideoFile, pk=video_pk)
    user = get_object_or_404(User, pk=request.user.pk)

    if video.author == user:
        if request.method == "POST":
            if "confirm" in request.POST:
                video.delete()
                return redirect("section", pk=course.pk, section_pk=section.pk)
        else:
            return render(
                request,
                "delete_video_confirmation.html",
                {"course": course, "current_section": section, "video": video},
            )
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
        {"course": course, "current_section": section, "video": video},
    )
