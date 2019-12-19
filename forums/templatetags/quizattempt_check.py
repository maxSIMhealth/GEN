from django import template

register = template.Library()


@register.simple_tag
def quizattempt_check(user, course, quiz):
    try:
        attempt_no = quiz.mcquestionattempt_set.filter(student=user, course=course, quiz=quiz).latest('attempt_no')
    except:
        attempt_no = 0 # this value isn't going to be used
        print("No quiz attempt found")
    return attempt_no
