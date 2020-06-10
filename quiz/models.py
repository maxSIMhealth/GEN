from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from model_utils.models import TimeStampedModel

from courses.models import Course, SectionItem
from videos.models import VideoFile

QUESTION_TYPES = [
    ("H", "Header"),
    ("L", "Likert"),
    ("O", "Open ended"),
    ("M", "Multiple choice"),
]


def duplicate_name(object):
    object.name += " (Copy)"
    return object


def duplicate(object, callback=None):
    """
    Based on: https://stackoverflow.com/a/52761222/2066218

    Duplicate a model instance, making copies of all foreign keys pointing to it.
    There are 3 steps that need to occur in order:

    1.  Enumerate the related child objects and m2m relations, saving in lists/dicts
    2.  Copy the parent object per django docs (doesn't copy relations)
    3a. Copy the child objects, relating to the copied parent object
    3b. Re-create the m2m relations on the copied parent object

    The optional callback function is called once the item has been duplicated but before
    it's saved. The new object is passed its only argument and it should return the object to be save.
    It can be used e.g. to update the name of the duplicated object

    ```
    def duplicate_name(object):
        object.name += ' (Copy)'
        return object

    duplicate(object, callback=duplicate_name)
    ```
    """
    related_objects_to_copy = []
    relations_to_set = {}

    # Iterate through all the fields in the parent object looking for related fields
    fields = object._meta.get_fields()
    for field in fields:
        if field.one_to_many:
            # One to many fields are backward relationships where many child
            # objects are related to the parent. Enumerate them and save a list
            # so we can copy them after duplicating our parent object.
            print(f"Found a one-to-many field: {field.name}")

            # 'field' is a ManyToOneRel which is not iterable, we need to get
            # the object attribute itself.
            related_object_manager = getattr(object, field.get_accessor_name())
            related_objects = list(related_object_manager.all())
            if related_objects:
                print(f" - {len(related_objects)} related objects to copy")
                related_objects_to_copy += related_objects

        elif field.one_to_one:
            if hasattr(object, field.name):
                # In testing, these relationships are not being copied automatically.
                print(f"Found a one-to-one field: {field.name}")
                related_object = getattr(object, field.name)
                related_objects_to_copy.append(related_object)

        elif field.many_to_one:
            # In testing, these relationships are preserved when the parent
            # object is copied, so they don't need to be copied separately.
            print(f"Found a many-to-one field: {field.name}")

        elif field.many_to_many and not hasattr(field, "field"):
            # Many to many fields are relationships where many parent objects
            # can be related to many child objects. Because of this the child
            # objects don't need to be copied when we copy the parent, we just
            # need to re-create the relationship to them on the copied parent.
            related_object_manager = getattr(object, field.name)

            if related_object_manager.through:
                # Many to many relations with a through table are handled as many to one relationships
                # between the object and the through table so we can skip this
                continue

            print(f"Found a many-to-many field: {field.name}")
            relations = list(related_object_manager.all())
            if relations:
                print(f" - {len(relations)} relations to set")
                relations_to_set[field.name] = relations

    # Duplicate the parent object
    # https://docs.djangoproject.com/en/3.0/topics/db/queries/#copying-model-instances
    object.pk = None
    object.id = None

    if callback and callable(callback):
        object = callback(object)

    object.save()
    print(f"Copied parent object ({str(object)})")

    # Copy the one-to-many child objects and relate them to the copied parent
    for related_object in related_objects_to_copy:
        # Iterate through the fields in the related object to find the one that
        # relates to the parent model.
        for related_object_field in related_object._meta.fields:
            if related_object_field.related_model == object.__class__ or (
                hasattr(related_object_field.related_model, "_meta")
                and related_object_field.related_model._meta.proxy_for_model
                == object.__class__
            ):
                # If the related_model on this field matches the parent
                # object's class, perform the copy of the child object and set
                # this field to the parent object, creating the new
                # child -> parent relationship.
                setattr(related_object, related_object_field.name, object)
                new_related_object = duplicate(related_object)
                new_related_object.save()

                text = str(related_object)
                text = (text[:40] + "..") if len(text) > 40 else text
                print(f"|- Copied child object ({text})")

    # Set the many-to-many relations on the copied parent
    for field_name, relations in relations_to_set.items():
        # Get the field by name and set the relations, creating the new
        # relationships.
        field = getattr(object, field_name)
        field.set(relations)
        text_relations = []
        for relation in relations:
            text_relations.append(str(relation))
        print(
            f"|- Set {len(relations)} many-to-many relations on {field_name} {text_relations}"
        )

    return object


class Quiz(SectionItem):
    """
    Quiz model
    """

    show_score = models.BooleanField(default=False)
    show_correct_answers = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="quizzes")
    video = models.ForeignKey(
        VideoFile,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="quizzes",
    )
    requirement = models.ForeignKey(
        "self", on_delete=models.PROTECT, blank=True, null=True
    )
    attempts_max_number = models.PositiveIntegerField(
        default=1, blank=False, null=False
    )

    class Meta:
        verbose_name_plural = "quizzes"

    def get_questions(self):
        return self.questions.all().select_subclasses()

    def duplicate_quiz(self):
        return duplicate(self, callback=duplicate_name)


class Question(TimeStampedModel):
    """
    Parent class for questions (Multiple Choice, Likert Scale and Open Ended)
    and for question headers.
    """

    question_type = models.CharField(max_length=1, choices=QUESTION_TYPES)
    quiz = models.ForeignKey(
        Quiz,
        verbose_name="Quiz",
        related_name="questions",
        blank=False,
        on_delete=models.CASCADE,
    )
    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the content that you want displayed.",
        verbose_name="Content",
    )
    explanation = models.TextField(
        blank=True,
        help_text="Explanation to be shown after the question has been answered.",
    )
    multiple_correct_answers = models.BooleanField(
        blank=False,
        default=False,
        help_text="Does this question have multiple correct answers \
            (allow user to select multiple answer items)?",
    )
    custom_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["custom_order"]

    def __str__(self):
        return self.content


class QuestionGroupHeaderManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(QuestionGroupHeaderManager, self)
            .get_queryset()
            .filter(question_type="H")
        )
        return queryset


class LikertManager(models.Manager):
    def get_queryset(self):
        queryset = super(LikertManager, self).get_queryset().filter(question_type="L")
        return queryset

    def create(self, **kwargs):
        kwargs.update({"question_type": "L"})
        return super(LikertManager, self).create(**kwargs)


class OpenEndedManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(OpenEndedManager, self).get_queryset().filter(question_type="O")
        )
        return queryset


class MCQuestionManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(MCQuestionManager, self).get_queryset().filter(question_type="M")
        )
        return queryset


class Likert(Question):
    """Likert Model"""

    objects = LikertManager()

    class Meta:
        proxy = True
        verbose_name = "Likert question"
        verbose_name_plural = "Likert questions"

    def get_answers(self):
        return LikertAnswer.objects.filter(question=self)

    def __str__(self):
        return ("%s") % (self.content)

    # def get_changeform_initial_data(self, request):
    #     return {"question_type": "L"}


class LikertAnswer(TimeStampedModel):
    """
    Likert answer (scale) model.
    Minimum and maximum values are used to generate the scale layout.
    """

    question = models.OneToOneField(Likert, on_delete=models.CASCADE)
    scale_min = models.PositiveIntegerField(default=1)
    scale_max = models.PositiveIntegerField(default=5)
    legend = models.TextField(
        blank=True, help_text="Legend for the likert scale values."
    )

    def __str__(self):
        return ("%s : scale %s to %s") % (
            self.question.content,
            self.scale_min,
            self.scale_max,
        )

    def clean(self):
        # Don't allow max scale to be equal of lower than min scale
        if self.scale_max <= self.scale_min:
            raise ValidationError(
                "Maximum scale value cannot be equal or lower than minimum scale value."
            )
        return super().clean()

    class Meta:
        verbose_name = "Likert answer (scale definition)"
        verbose_name_plural = "Likert answers (scale definition)"


class OpenEnded(Question):
    """
    Open Ended model
    """

    objects = OpenEndedManager()

    # def __str__(self):
    #     return ("%s") % (self.content)

    class Meta:
        proxy = True
        verbose_name = "Open ended question"
        verbose_name_plural = "Open ended questions"


class MCQuestion(Question):

    objects = MCQuestionManager()

    class Meta:
        proxy = True
        verbose_name = "Multiple choice question"
        verbose_name_plural = "Multiple choice questions"

    def check_if_correct(self, guess):
        answer = MCAnswer.objects.get(id=guess)

        return bool(answer.correct)

    def get_answers(self):
        return MCAnswer.objects.filter(question=self)

    def get_answers_list(self):
        return [
            (answer.id, answer.content)
            for answer in MCAnswer.objects.filter(question=self)
        ]


class MCAnswer(TimeStampedModel):
    """
    Multiple choice question answer
    """

    question = models.ForeignKey(
        MCQuestion, on_delete=models.CASCADE, related_name="answers"
    )

    content = models.CharField(
        max_length=1000,
        blank=False,
        help_text="Enter the answer text that you want displayed",
    )

    correct = models.BooleanField(
        blank=False, default=False, help_text="Is this the correct answer?"
    )

    custom_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "Multiple choice answer"
        verbose_name_plural = "Multiple choice answers"
        ordering = ["custom_order"]


class QuestionAttempt(TimeStampedModel):
    question_type = models.CharField(max_length=1, choices=QUESTION_TYPES)
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    attempt_number = models.PositiveIntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    video = models.ForeignKey(
        VideoFile, blank=True, null=True, on_delete=models.PROTECT
    )
    answer_content = models.TextField(("student answer"), null=True, blank=True)
    correct = models.NullBooleanField(blank=True, null=True)
    # likert_answer_content = models.PositiveIntegerField(blank=True, null=True)
    multiplechoice_answer = models.ForeignKey(
        MCAnswer, blank=True, null=True, on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "Question attempt"
        verbose_name_plural = "Question attempts"

    def __str__(self):
        return "%s - %s - Course %s (attempt %s): %s" % (
            self.student.get_full_name(),
            self.quiz.name,
            self.course.name,
            self.attempt_number,
            self.question,
        )


class LikertAttemptManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(LikertAttemptManager, self).get_queryset().filter(question_type="L")
        )
        return queryset

    def create(self, **kwargs):
        kwargs.update({"question_type": "L"})
        return super(LikertAttemptManager, self).create(**kwargs)


class OpenEndedAttemptManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(OpenEndedAttemptManager, self)
            .get_queryset()
            .filter(question_type="O")
        )
        return queryset

    def create(self, **kwargs):
        kwargs.update({"question_type": "O"})
        return super(OpenEndedAttemptManager, self).create(**kwargs)


class MCQuestionAttemptManager(models.Manager):
    def get_queryset(self):
        queryset = (
            super(MCQuestionAttemptManager, self)
            .get_queryset()
            .filter(question_type="M")
        )
        return queryset

    def create(self, **kwargs):
        kwargs.update({"question_type": "M"})
        return super(MCQuestionAttemptManager, self).create(**kwargs)


class LikertAttempt(QuestionAttempt):
    """
    Likert Attempt model
    """

    objects = LikertAttemptManager()

    class Meta:
        proxy = True
        verbose_name = "Likert attempt"
        verbose_name_plural = "Likert attempts"


class OpenEndedAttempt(QuestionAttempt):
    """
    Open Ended Attempt model
    """

    objects = OpenEndedAttemptManager()

    class Meta:
        proxy = True
        verbose_name = "Open ended attempt"
        verbose_name_plural = "Open ended attempts"


class MCQuestionAttempt(QuestionAttempt):
    """
    Multiple Choice Attempt model
    """

    objects = MCQuestionAttemptManager()

    class Meta:
        proxy = True
        verbose_name = "Multiple choice questions attempt"
        verbose_name_plural = "Multiple choice questions attempts"


class QuizScore(models.Model):
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "Score for user %s - quiz %s - course %s" % (
            self.student.username,
            self.quiz.name,
            self.course.name,
        )


class QuestionGroupHeader(Question):
    objects = QuestionGroupHeaderManager()

    class Meta:
        proxy = True

    def __str__(self):
        return self.content
