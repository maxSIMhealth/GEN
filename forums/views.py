

from urllib.parse import urlparse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
# from django.core.files import File
# from django.core.files.storage import FileSystemStorage
# from django.core.files.images import ImageFile
# from django.views.generic import ListView
from django.utils import timezone

from courses.models import Course, User
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
    user = request.user

    # filter videos submitted by instructors
    course_instructors = course.instructors.all()
    course_videos = course.videos.filter(author__in=course_instructors)

    # checks if the current user is a course instructor
    if course in user.instructor.all():
        # returns all participants videos to the instructor (excluding his own)
        user_videos = course.videos.exclude(author=user)
    else:
        # returns only videos submitted by current user
        user_videos = user.videos.get_queryset()

    # TODO: old code, check if it should be deleted
    # media_list = []
    # for forum in forums:
    #     if forum.media.kind == 'YTB':
    #         media_list.append(forum)

    return render(request, 'list_videos.html',
                  {'course': course,
                   'forums': forums,
                   'course_videos': course_videos,
                   'user_videos': user_videos})


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
    quizzes = course.quizzes.all().filter(published=True)

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
            return redirect('list_videos', pk=course.pk)
    else:
        form = UploadVideoForm()

    return render(request, 'upload_video.html', {
        'form': form,
        'course': course,
        'forums': forums
    })


@login_required
def delete_video(request, pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    video = get_object_or_404(VideoFile, pk=video_pk)
    user = get_object_or_404(User, pk=request.user.pk)

    if video.author == user:
        if request.method == 'POST':
            if 'confirm' in request.POST:
                video.delete()
                return redirect('list_videos', pk=course.pk)
        else:
            return render(request, 'delete_video_confirmation.html', {
                'course': course,
                'video': video
            })
    else:
        return render(request, 'permission_error.html')


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
def video_player(request, pk, video_pk):
    course = get_object_or_404(Course, pk=pk)
    video = get_object_or_404(VideoFile, pk=video_pk)

    return render(request, 'video_player.html',
                  {'course': course,
                   'video': video})


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
