from django import template
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