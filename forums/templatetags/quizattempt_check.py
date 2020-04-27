from django import template

register = template.Library()


@register.simple_tag
def quizattempt_check(user, course, quiz):
    try:
        attempt_number = quiz.mcquestionattempt_set.filter(
            student=user, course=course, quiz=quiz).latest('attempt_number')
    except:
        attempt_number = 0  # this value isn't going to be used
        print("No quiz attempt found")
    return attempt_number
