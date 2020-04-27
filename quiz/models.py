from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel
from model_utils.managers import InheritanceManager

from forums.models import Course, VideoFile


class Quiz(TimeStampedModel):
    """
    Quiz model
    """

    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='quizzes')
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='quizzes')
    video = models.ForeignKey(
        VideoFile, on_delete=models.PROTECT, related_name='quizzes')

    class Meta:
        verbose_name_plural = "quizzes"

    def get_questions(self):
        return self.questions.all().select_subclasses()

    def __str__(self):
        return self.name


class Question(TimeStampedModel):
    """
    Question model
    Parent for Multiple Choice, Likert Scale and Open Ended questions
    """

    quiz = models.ManyToManyField(
        Quiz,
        verbose_name='Quiz',
        related_name='questions',
        blank=True)
    # on_delete=models.PROTECT)
    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the question text that you want displayed ",
        verbose_name="Question")
    explanation = models.TextField(
        blank=True,
        help_text="Explanation to be shown after the question has been answered.")

    objects = InheritanceManager()

    def __str__(self):
        return self.content


class Likert(Question):
    """Likert Model"""

    def __str__(self):
        return ("%s") % (self.content)

    class Meta:
        verbose_name = "Likert scale question"
        verbose_name_plural = "Likert scale questions"


class LikertAnswer(TimeStampedModel):
    """
    Likert Answer Model
    """

    # SCALE_CHOICES = (
    #     ('', ''),
    #     ('0', '0'),
    #     ('1', '1'),
    #     ('2', '2'),
    #     ('3', '3'),
    #     ('4', '4'),
    #     ('5', '5'),
    # )

    question = models.OneToOneField(Likert, on_delete=models.PROTECT)
    scale_min = models.PositiveIntegerField(default=1)
    scale_max = models.PositiveIntegerField(default=5)
    # correct = models.CharField(max_length=2,
    #                            choices=SCALE_CHOICES,
    #                            blank=True,
    #                            null=True,
    #                            default='')

    def __str__(self):
        return ("%s : %s to %s") % (self.question.content, self.scale_min, self.scale_max)

    class Meta:
        verbose_name = 'Likert answer'
        verbose_name_plural = 'Likert answers'


class LikertAttempt(TimeStampedModel):
    """
    Liket Attempt model
    """

    SCALE_CHOICES = (
        ('', ''),
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    )

    likert = models.ForeignKey(Likert, on_delete=models.PROTECT)
    student = models.ForeignKey(User, on_delete=models.PROTECT)

    correct = models.NullBooleanField(blank=True, null=True)
    attempt_number = models.PositiveIntegerField(default=0)
    scale = models.CharField(max_length=2,
                             choices=SCALE_CHOICES,
                             blank=True,
                             null=True,
                             default='')

    def __str__(self):
        return ("%s_%s_%s") % (self.student.username, self.likert.quiz, self.attempt_number)

    class Meta:
        verbose_name = "likert scale attempt"
        verbose_name_plural = "likert scale attempts"


class OpenEnded(Question):
    """
    Open Ended model
    """

    # def __str__(self):
    #     return ("%s") % (self.content)

    class Meta:
        verbose_name = "Open ended Question"
        verbose_name_plural = "Open ended questions"


class OpenEndedAttempt(TimeStampedModel):
    """
    Open Ended Attempt model
    """

    openended = models.ForeignKey(OpenEnded, on_delete=models.PROTECT)
    student = models.ForeignKey(User, on_delete=models.PROTECT)

    answer = models.TextField(('answer'), null=True, blank=True)
    attempt_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return ("%s_%s_%s") % (self.student.get_full_name(), self.openended.quiz, self.attempt_number)

    class Meta:
        verbose_name = "open ended attempt"
        verbose_name_plural = "open ended attempts"


class MCQuestion(Question):
    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)

        return bool(answer.correct)

    def get_answers(self):
        return Answer.objects.filter(question=self)

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                Answer.objects.filter(question=self)]

    class Meta:
        verbose_name = "Multiple Choice Question"
        verbose_name_plural = "Multiple Choice Questions"


class Answer(models.Model):
    question = models.ForeignKey(
        MCQuestion,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the answer text that you want displayed"
    )

    correct = models.BooleanField(
        blank=False,
        default=False,
        help_text="Is this the correct answer?"
    )

    def __str__(self):
        return self.content


class MCQuestionAttempt(TimeStampedModel):
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    question = models.ForeignKey(MCQuestion, on_delete=models.PROTECT)
    correct = models.NullBooleanField(blank=True, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.PROTECT)
    answer_content = models.CharField('student answer', max_length=1000)
    attempt_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "User %s - quiz %s - course %s - attempt %s - answer id %s" % \
            (self.student.username,
             self.quiz.name,
             self.course.name,
             self.attempt_number,
             self.answer_id)

    class Meta:
        verbose_name = "Multiple Choice Questions Attempt"
        verbose_name_plural = "Multiple Choice Questions Attempts"


class QuizScore(models.Model):
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Score for user %s - quiz %s - course %s" % \
            (self.student.username,
             self.quiz.name,
             self.course.name)
