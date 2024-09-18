from django.utils.decorators import method_decorator

from courses.models import Course, Section, User
from discussions.models import Discussion

import boto3
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic
from GEN.decorators import course_enrollment_check
from GEN.support_methods import enrollment_test

from .forms import UploadVideoForm
from .models import VideoFile


decorators=[login_required, course_enrollment_check(enrollment_test)]

@method_decorator(decorators, name='dispatch')
class UploadVideoView(generic.CreateView):
    model = VideoFile
    form_class = UploadVideoForm
    template_name = 'videos/upload_video.html'
    success_url = '/'

    # def __init__(self, **kwargs):
    #     super().__init__(kwargs)
    #     self.course = None
    #     self.section = None

    def dispatch(self, request, *args, **kwargs):
        # Initialize course and section here
        self.course = get_object_or_404(Course, pk=self.kwargs["pk"])
        self.section = get_object_or_404(Section, pk=self.kwargs["section_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use instance variables set in dispatch
        context["course"] = self.course
        context["section"] = self.section
        return context

    def get_success_url(self):
        course_pk = self.object.course.pk
        section_pk = self.object.section.pk

        messages.success(self.request, _("Upload successful."))

        return reverse("section", args=[course_pk, section_pk])

    def form_valid(self, form):
        user = self.request.user

        # Use instance variables set in dispatch
        form.instance.author = user
        form.instance.course = self.course
        form.instance.section = self.section

        return super().form_valid(form)


@login_required
@course_enrollment_check(enrollment_test)
def upload_video(request, pk, section_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    allow_submission = False

    # check if user is a course instructor
    is_instructor = bool(course in request.user.instructor.all())

    # check if section type is upload
    if section.section_type == "U":
        if is_instructor:
            messages.error(
                request,
                _("Only learners are allowed to upload in this section."),
            )
            return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
        section_items = section.section_items.filter(author=request.user)
        if not section_items:
            allow_submission = True
    elif section.section_type == "V":
        if is_instructor:
            allow_submission = True
    else:
        messages.error(
            request,
            _("This section does not support uploads."),
        )
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
        # raise Http404("This section does not support uploads.")

    if allow_submission:
        if request.method == "POST":
            form = UploadVideoForm(
                request.POST, request.FILES, blind_data=course.blind_data
            )

            # if "Cancel" in request.POST["submit"]:
            #     return redirect("section", pk=course.pk, section_pk=section.pk)
            if form.is_valid():
                video = VideoFile.objects.populate(True).create(
                    name=form.cleaned_data.get("name"),
                    description=form.cleaned_data.get("description"),
                    author=request.user,
                    course=course,
                    file=form.files.get("file"),
                    section=section,
                    mute_audio=section.mute_audio,
                    # if instructor, the video gets published
                    published=False,
                )
                video.save()
                messages.success(request, _("Upload successful."))
                return redirect("section", pk=course.pk, section_pk=section.pk)
        else:
            if course.blind_data:
                video_name = "User video (blind data)"
                video_description = "No description"
                form = UploadVideoForm(
                    initial={"name": video_name, "description": video_description},
                    blind_data=course.blind_data,
                )
            else:
                form = UploadVideoForm(
                    blind_data=course.blind_data,
                )

        return render(
            request,
            "videos/upload_video.html",
            {"form": form, "course": course, "section": section},
        )
    else:
        messages.error(
            request,
            _("You don't have permission to upload."),
        )
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
        # raise Http404("You don't have permission to upload.")


@login_required
@course_enrollment_check(enrollment_test)
def publish_video(request, pk, section_pk, sectionitem_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    video = get_object_or_404(VideoFile, pk=sectionitem_pk)
    user = get_object_or_404(User, pk=request.user.pk)

    if video.published:
        messages.warning(
            request,
            _("The video is already published."),
        )
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
    elif video.author == user:
        if request.method == "POST":
            if "confirm" in request.POST:
                video.published = True
                video.save()

                # if section has parameter 'create_discussion' enabled, create
                # a discussion using the video's parameters and put it on the
                # 'section_output'
                if section.create_discussions:
                    discussion = Discussion.objects.create(
                        course=course,
                        section=section.section_output,
                        access_restriction=section.output_access_restriction,
                        author_access_override=section.output_author_access_override,
                        published=True,
                        name=video.name,
                        description=video.description,
                        video=video,
                        author=request.user,
                    )
                    discussion.save()

                # if section has parameter 'clone_quiz' enabled, clone the reference
                # quiz and set cloned quiz video parameter as the uploaded video
                if section.clone_quiz:
                    cloned_quiz = section.clone_quiz_reference.duplicate()
                    # setting uploaded video as the cloned quiz video
                    cloned_quiz.video = video
                    # setting quiz parameters to the current course (since the reference probably has different values)
                    cloned_quiz.course = course
                    cloned_quiz.section = section.clone_quiz_output_section
                    if section.clone_quiz_update_owner:
                        cloned_quiz.author = request.user
                    # making sure that the quiz is set to published
                    cloned_quiz.published = True
                    cloned_quiz.save()
                    # set cloned_quiz section as not completed to all users
                    # FIXME: find a better way to set status for sections that have user-submitted content
                    if cloned_quiz.section:
                        output_section_status_list = cloned_quiz.section.status.all()
                        for status in output_section_status_list:
                            status.completed = False
                            status.save()

                # set section Status object as completed
                section_status = section.status.filter(learner=user).get()
                section_status.completed = True
                section_status.save()

                return redirect("section", pk=course.pk, section_pk=section.pk)
        else:
            return render(
                request,
                "videos/publish_video_confirmation.html",
                {"course": course, "section": section, "video": video},
            )
    else:
        messages.error(
            request,
            _("You don't have permission to do that."),
        )
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))


@login_required
@course_enrollment_check(enrollment_test)
def unpublish_video(request, pk, section_pk, sectionitem_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    video = get_object_or_404(VideoFile, pk=sectionitem_pk)
    user = get_object_or_404(User, pk=request.user.pk)

    # check if user is a course instructor
    is_instructor = bool(course in request.user.instructor.all())

    if not is_instructor:
        messages.error(
            request,
            _("You don't have permission to do that."),
        )
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
    elif not video.published:
        messages.warning(
            request,
            _("The requested video is already unpublished."),
        )
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
    elif video.author == user:
        if request.method == "POST":
            if "confirm" in request.POST:
                video.published = False
                video.save()
                return redirect("section", pk=course.pk, section_pk=section.pk)
        else:
            return render(
                request,
                "videos/unpublish_video_confirmation.html",
                {"course": course, "section": section, "video": video},
            )
    else:
        messages.error(
            request,
            _("You don't have permission to do that."),
        )
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))


@login_required
@course_enrollment_check(enrollment_test)
def delete_video(request, pk, section_pk, sectionitem_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    video = get_object_or_404(VideoFile, pk=sectionitem_pk)
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
                    "videos/delete_video_confirmation.html",
                    {"course": course, "section": section, "video": video},
                )
        else:
            messages.error(
                request,
                _("You don't have permission to do that."),
            )
            return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))
    else:
        messages.error(
            request,
            _("You don't have permission to do that."),
        )
        return HttpResponseRedirect(reverse("section", args=[pk, section.pk]))


@login_required
@course_enrollment_check(enrollment_test)
def video_player(request, pk, section_pk, sectionitem_pk):
    course = get_object_or_404(Course, pk=pk)
    section = get_object_or_404(Section, pk=section_pk)
    video = get_object_or_404(VideoFile, pk=sectionitem_pk)
    user = get_object_or_404(User, pk=request.user.pk)

    if video.published or user == video.author:
        return render(
            request,
            "videos/video_player.html",
            {"course": course, "section": section, "video": video},
        )
    else:
        raise Http404("This video is not published.")

# @method_decorator(login_required, name="dispatch")
class SignedURLView(generic.View):
    def post(self, request, *args, **kwargs):
        session = boto3.session.Session()
        client = session.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        user = get_object_or_404(User, pk=request.user.pk)

        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        url = client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
              "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
              "Key": f"{settings.AWS_LOCATION}/media/private/user_{user.id}/{json.loads(request.body)['fileName']}",
            },
            ExpiresIn=300,
        )
        return JsonResponse({"url": url})
