from django import template
from django.db.models import Count

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
def rank(user_id, course_id, kind):
    forums = Forum.objects.all()

    if kind == 'forum':

        # get forums by authors (username), counts the likes (votes)
        # and order them from highest to lowest
        items = forums.values('author__username').annotate(Count('votes')).order_by('-votes__count')
        # filter the forum list to the current user id
        # (list is empty if the user never created a forum)
        item_user = items.filter(author=user_id)

        # check if user created a forum
        if item_user.exists():
            # get user forum vote score and check if there are
            # other forums with higher scores
            # (list begins with 0, that's why I add 1)
            rank_user = items.filter(votes__count__gt=item_user[0]['votes__count']).count() + 1
        else:
            # otherwise, the user never created a forum and so
            # the rank position is 0
            rank_user = 0

    return rank_user


@register.simple_tag
def rank_course(user_id, course_id, kind):
    forums = Forum.objects.filter(course=course_id)
    # username = User.objects.get(pk=user_id).username
    # rank = 0
    # rank_user = 0

    if kind == 'forum':

        # get forums by authors (username), counts the likes (votes)
        # and order them from highest to lowest
        items = forums.values('author__username').annotate(Count('votes')).order_by('-votes__count')
        # filter the forum list to the current user id
        # (list is empty if the user never created a forum)
        item_user = items.filter(author=user_id)

        # check if user created a forum
        if item_user.exists():
            # get user forum vote score and check if there are
            # other forums with higher scores
            # (list begins with 0, that's why I add 1)
            rank_user = items.filter(votes__count__gt=item_user[0]['votes__count']).count() + 1
        else:
            # otherwise, the user never created a forum and so
            # the rank position is 0
            rank_user = 0

        # alternative method, but using a for isn't a good pratice
        # because it would check every item in the list
        # rank_user = items.filter(votes__count__gt=item['votes__count']).count() + 1

        # items = forums.values('author__username').annotate(Count('votes')).order_by('-votes__count')
        # for item in items:
        #     rank += 1
        #     print(item['author__username'])
        #     if item['author__username'] == username:
        #         rank_user = rank

    return rank_user
