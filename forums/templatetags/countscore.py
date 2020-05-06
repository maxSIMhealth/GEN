from django import template
from django.db.models import Count
from django.contrib.auth.models import User

from forums.models import Forum, Comment
from quiz.models import QuizScore

register = template.Library()


def countitem_score(items, current_score):
    score = current_score

    for item in items:
        # for forums and comments votes
        if hasattr(item, 'votes'):
            score += item.votes.count()
        # for quiz scores
        elif hasattr(item, 'score'):
            score += item.score

    return score


@register.simple_tag
def countscore(user_id, kind):
    score = 0

    if kind == "forum":
        items = Forum.objects.filter(author=user_id)
    elif kind == "comment":
        items = Comment.objects.filter(author=user_id)
    elif kind == "quiz":
        items = QuizScore.objects.filter(student=user_id)

    score = countitem_score(items, score)

    return score


@register.simple_tag
def countscore_course(user_id, course_id, kind):
    forums = Forum.objects.filter(author=user_id, course=course_id)
    quizzes = QuizScore.objects.filter(student=user_id, course=course_id)
    score = 0

    if kind == "forum":
        items = forums
        score = countitem_score(items, score)
    elif kind == "comment":
        for forum in forums:
            if Comment.objects.filter(author=user_id, forum=forum.id).exists():
                items = Comment.objects.filter(author=user_id, forum=forum.id)
                score = countitem_score(items, score)
    elif kind == "quiz":
        items = quizzes
        score = countitem_score(items, score)

    return score


@register.simple_tag
def rank_get(user_id, course_id, kind):
    # dashboard/home has no course_id
    if course_id is None:
        forums = Forum.objects.all()
        quizscore = QuizScore.objects.all()
    else:
        forums = Forum.objects.filter(course=course_id)
        quizscore = QuizScore.objects.filter(course=course_id)
    username = User.objects.get(pk=user_id).username
    rank = 0
    rank_user = 0

    if kind == 'forum':
        if forums.exists():
            # get forums by authors (username), counts the likes (votes)
            # and order them from highest to lowest
            items = forums.values('author__username').annotate(
                Count('votes')).order_by('-votes__count')

    elif kind == 'comment':
        counter = 0

        if forums.exists():
            for forum in forums:
                if counter == 0:
                    items = forum.comments.values(
                        'author__username').annotate(Count('votes'))
                else:
                    items = items | forum.comments.values(
                        'author__username').annotate(Count('votes'))
                counter += 1

            items = items.order_by('-votes__count')

    elif kind == 'quiz':
        if quizscore.exists():
            items = quizscore.values('student').annotate(
                Count('score')).order_by('-score__count')

    # check if variable 'items' exists
    if 'items' in locals():
        for item in items:
            rank += 1
            if kind == 'quiz':
                if item['student'] == user_id:
                    rank_user = rank
            else:
                if item['author__username'] == username:
                    rank_user = rank
    # except:
    #     rank_user = 0

    return rank_user
