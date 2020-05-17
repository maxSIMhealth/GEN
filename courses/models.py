from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Course(models.Model):
    name = models.CharField(
        max_length=100, unique=True, help_text=_("Course name (max 100 characters)")
    )
    code = models.CharField(
        "course code", max_length=10, help_text=_("Course code (max 10 characters)")
    )
    description = models.CharField(
        max_length=400, help_text=_("Course description (max 400 characters)")
    )
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="course")
    start_date = models.DateTimeField("start date", blank=True, null=True)
    end_date = models.DateTimeField("end date", blank=True, null=True)
    students = models.ManyToManyField(User, related_name="member")
    instructors = models.ManyToManyField(User, related_name="instructor")
    enable_gamification = models.BooleanField(
        "gamification",
        default=True,
        help_text=_("Enables voting in forums and comments"),
    )
    show_scoreboard = models.BooleanField(
        default=True, help_text=_("Requires gamification")
    )
    show_leaderboard = models.BooleanField(
        default=True, help_text=_("Requires gamification")
    )
    show_progress_tracker = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def clean(self):
        # check course dates
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError(
                    _(
                        "Course end date can not be equal or \
                                earlier than the start date."
                    )
                )
        # check gamification components
        if self.show_scoreboard and not self.enable_gamification:
            raise ValidationError(_("Scoreboard requires gamification to be enabled"))
        if self.show_leaderboard and not self.enable_gamification:
            raise ValidationError(_("Leaderboard requires gamification to be enabled"))
