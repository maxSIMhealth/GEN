import os
import io
import tempfile

from urllib.parse import urlparse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
# from django.core.files import File
# from django.core.files.storage import FileSystemStorage
# from django.core.files.images import ImageFile
# from django.views.generic import ListView
from django.utils import timezone
from PIL import Image

import ffmpeg

from courses.models import Course
from .forms import NewForumForm, NewCommentForm, UploadVideoForm
from .models import Forum, Comment, VideoFile


@login_required
def course_forums(request, pk):
    course = get_object_or_404(Course, pk=pk)
    forums = course.forums.all()
    gamification = False

    if settings.GAMIFICATION:
        gamification = True

    return render(request, 'course_forums.html',
                  {'course': course, 'forums': forums, 'gamification': gamification})


@login_required
def list_videos(request, pk):
    course = get_object_or_404(Course, pk=pk)
    forums = course.forums.all()
    videos = course.videos.all()
    # media_list = []

    # for forum in forums:
    #     if forum.media.kind == 'YTB':
    #         media_list.append(forum)

    return render(request, 'list_videos.html',
                  {'course': course, 'forums': forums, 'videos': videos})


@login_required
def list_pdfs(request, pk):
    course = get_object_or_404(Course, pk=pk)
    forums = course.forums.all()
    media_list = []

    for forum in forums:
        if forum.media.kind == 'PDF':
            media_list.append(forum)

    return render(request, 'list_pdfs.html',
                  {'course': course, 'forums': forums, 'media_list': media_list})


@login_required
def list_quiz(request, pk):
    course = get_object_or_404(Course, pk=pk)
    quizzes = course.quizzes.all()

    return render(request, 'list_quiz.html',
                  {'course': course, 'quizzes': quizzes})


# class ForumListView(ListView):
    # https://ccbv.co.uk/projects/Django/2.1/django.views.generic.list/ListView/
    # Render some list of objects, set by `self.model` or `self.queryset`.
    # `self.queryset` can actually be any iterable of items, not just a queryset.
    # model = Forum
    # context_object_name = 'forums'
    # template_name = 'home.html'


@login_required
def forum_comments(request, pk, forum_pk):
    course = get_object_or_404(Course, pk=pk)
    forum = get_object_or_404(Forum, pk=forum_pk)
    video = forum.video
    gamification = False

    if settings.GAMIFICATION:
        gamification = True

    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            forum.last_updated = timezone.now()
            forum.save()
            comment = Comment.objects.create(
                message=form.cleaned_data.get('message'),
                forum=forum,
                author=request.user
            )
            comment.save()
            my_kwargs = dict(
                pk=course.pk,
                forum_pk=forum.pk
            )
            return redirect('forum_comments', **my_kwargs)
    else:
        form = NewCommentForm()

    return render(request, 'comments.html',
                  {'forum': forum,
                   'course': course,
                   'video': video,
                   'form': form,
                   'gamification': gamification})


@login_required
def new_forum(request, pk):
    course = get_object_or_404(Course, pk=pk)
    forums = Forum.objects.all()

    if request.method == 'POST':
        form = NewForumForm(request.POST)
        if 'Cancel' in request.POST['submit']:
            return redirect('course_forums', pk=course.pk)
        if 'submit' in request.POST and form.is_valid():
            forum = Forum.objects.create(
                course=course,
                name=form.cleaned_data.get('name'),
                description=form.cleaned_data.get('description'),
                video=form.cleaned_data.get('video'),
                author=request.user
            )
            forum.save()
            return redirect('course_forums', pk=course.pk)
        # media_form = NewMediaForm(request.POST)
        # if form.is_valid() and media_form.is_valid():
        #     media = MediaFile.objects.create(
        #         title=media_form.cleaned_data.get('title'),
        #         kind=media_form.cleaned_data.get('kind'),
        #         author=request.user,
        #         url=media_form.cleaned_data.get('url'),
        #     )
        #     forum = Forum.objects.create(
        #         course=course,
        #         name=form.cleaned_data.get('name'),
        #         description=form.cleaned_data.get('description'),
        #         media=media,
        #         author=request.user
        #     )
        #     media.save()
        #     forum.save()
        #     return redirect('course_forums', pk=course.pk)
    else:
        form = NewForumForm()
        # media_form = NewMediaForm()

    # return render(request, 'new_forum.html', {'forums': forums, 'course': course, 'form': form, 'media_form': media_form})
    return render(request, 'new_forum.html', {'forums': forums, 'course': course, 'form': form})


@login_required
def upload_video(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # FIXME: the forums object will probably have to be removed later on
    forums = course.forums.all()

    if request.method == 'POST':
        form = UploadVideoForm(request.POST, request.FILES)

        if 'Cancel' in request.POST['submit']:
            return redirect('list_videos', pk=course.pk)
        if 'submit' in request.POST and form.is_valid():
            video = VideoFile.objects.create(
                title=form.cleaned_data.get('title'),
                description=form.cleaned_data.get('description'),
                author=request.user,
                course=course,
                file=form.files.get('file')
            )
            forum = Forum.objects.create(
                course=course,
                name=form.cleaned_data.get('title'),
                description=form.cleaned_data.get('description'),
                video=video,
                author=request.user
            )
            video.save()
            # generates thumbnail and store in a temporary file
            (thumbnail_filename, thumbnail_tempfile) = video_generate_thumbnail(video.pk)
            # save thumbnail file in user directory and link it to video object
            video.thumbnail.save(thumbnail_filename, thumbnail_tempfile)
            # closes temporary file and allows it to be deleted
            thumbnail_tempfile.close()
            forum.save()
            return redirect('list_videos', pk=course.pk)
    else:
        form = UploadVideoForm()

    return render(request, 'upload_video.html', {
        'form': form,
        'course': course,
        'forums': forums
    })


def read_frame_as_jpeg(in_filename, time):
    # based on: https://github.com/kkroening/ffmpeg-python/blob/master/examples/read_frame_as_jpeg.py
    out, err = (
        ffmpeg
        .input(in_filename, ss=time)
        # .filter('select', 'gte(n,{})'.format(frame_num))
        .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
        .run(capture_stdout=True)
    )
    return (out, err)


def video_generate_thumbnail(video_pk):
    """Generates video thumbnail (square proportion)"""
    video = get_object_or_404(VideoFile, pk=video_pk)
    video_path = '.' + video.file.url
    video_filename = os.path.splitext(video.file.name)[0]
    thumbnail_filename = os.path.split(video_filename)[1] + '_thumb.jpg'
    ffmpeg_tempfile = tempfile.NamedTemporaryFile()
    # video_thumbnail_output = '.' + settings.MEDIA_URL + thumbnail_filename
    size = (128, 128)

    (ffmpeg_output, ffmpeg_error) = read_frame_as_jpeg(video_path, '00:00:01.000')

    if ffmpeg_error is None:
        print('Thumbnail generated ok')
        thumbnail = Image.open(io.BytesIO(ffmpeg_output))
        thumbnail = crop_image(thumbnail)
        thumbnail.thumbnail(size)
        thumbnail.save(ffmpeg_tempfile, 'JPEG')
        ffmpeg_tempfile.seek(0)
        print('Thumbnail resized ok')
    else:
        raise ValueError('Error generating thumbnail:' + ffmpeg_error)

    return (thumbnail_filename, ffmpeg_tempfile)


def crop_image(image):
    """Generates a square cropped image based on its center"""
    width, height = image.size

    if width != height:
        if width > height:
            crop = (width - height) / 2
            left = crop
            top = 0
            right = height + crop
            bottom = height
        elif width < height:
            crop = (height - width) / 2
            left = 0
            top = crop
            right = width
            bottom = width + crop

        result = image.crop((left, top, right, bottom))
    else:
        result = image

    return result


@login_required
def video_comments(request, pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    forums = course.forums.all()
    video = get_object_or_404(VideoFile, pk=video_pk)
    forum = forums.filter(name=video.title)[0]
    gamification = False

    if settings.GAMIFICATION:
        gamification = True

    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            forum.last_updated = timezone.now()
            forum.save()
            comment = Comment.objects.create(
                message=form.cleaned_data.get('message'),
                forum=forum,
                author=request.user
            )
            comment.save()
            my_kwargs = dict(
                pk=course.pk,
                video_pk=video.pk
            )
            return redirect('video_comments', **my_kwargs)
    else:
        form = NewCommentForm()

    return render(request, 'video_comments.html',
                  {'forum': forum,
                   'course': course,
                   'video': video,
                   'form': form,
                   'gamification': gamification})


@login_required
def upvote_forum(request, pk, forum_pk):
    course = get_object_or_404(Course, pk=pk)
    forum = Forum.objects.get(pk=forum_pk)
    forum.votes.up(request.user.id)

    # checking if the user is voting from the forums list or from forum itself
    path = urlparse(request.META['HTTP_REFERER']).path + "upvote"

    my_kwargs = dict(
        pk=course.pk,
        forum_pk=forum.pk
    )

    if request.path == path:
        return redirect('forum_comments', **my_kwargs)
    else:
        return redirect('course_forums', pk=course.pk)


@login_required
def clearvote_forum(request, pk, forum_pk):
    course = get_object_or_404(Course, pk=pk)
    forum = Forum.objects.get(pk=forum_pk)
    forum.votes.delete(request.user.id)

    # checking if the user is voting from the forums list or from forum itself
    path = urlparse(request.META['HTTP_REFERER']).path + "clearvote"

    my_kwargs = dict(
        pk=course.pk,
        forum_pk=forum.pk
    )

    if request.path == path:
        return redirect('forum_comments', **my_kwargs)
    else:
        return redirect('course_forums', pk=course.pk)


@login_required
def upvote_comment(request, pk, forum_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.votes.up(request.user.id)

    my_kwargs = dict(
        pk=pk,
        forum_pk=forum_pk
    )

    return redirect('forum_comments', **my_kwargs)


@login_required
def clearvote_comment(request, pk, forum_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    comment.votes.delete(request.user.id)

    my_kwargs = dict(
        pk=pk,
        forum_pk=forum_pk
    )

    return redirect('forum_comments', **my_kwargs)
