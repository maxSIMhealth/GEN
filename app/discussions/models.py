from courses.models import Course, SectionItem
from model_utils.models import TimeStampedModel
from videos.models import VideoFile
from vote.models import VoteModel

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from GEN.support_methods import duplicate_object


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.author.id, filename)


class Discussion(VoteModel, SectionItem):
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="discussions",
        verbose_name=_("course"),
    )
    last_updated = models.DateTimeField(_("last updated"), auto_now_add=True)
    # FIXME: media should be renamed to document or something like that
    # media = models.ForeignKey(
    #     MediaFile, on_delete=models.CASCADE, related_name='discussions')
    requirement = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("requirement"),
    )
    video = models.ForeignKey(
        VideoFile,
        on_delete=models.CASCADE,
        related_name="discussions",
        blank=True,
        null=True,
        verbose_name=_("video"),
    )

    class Meta:
        verbose_name = _("discussion")
        verbose_name_plural = _("discussions")

    def get_comment_count(self):
        return Discussion.objects.filter(comments__discussion=self).count()

    def save(self, *args, **kwargs):
        self.item_type = SectionItem.SECTION_ITEM_DISCUSSION
        super().save(*args, **kwargs)

    def duplicate(self, **kwargs):
        return duplicate_object(self, **kwargs)


class Comment(VoteModel, TimeStampedModel):
    message = models.TextField(_("message"), max_length=400)
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("discussion"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("author"),
    )

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        ordering = ["created"]

    def __str__(self):
        return self.message
