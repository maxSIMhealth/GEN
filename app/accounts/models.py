from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from courses.models import Course


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("user"))
    # bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(_("location"), max_length=30, blank=True)
    institution = models.CharField(_("institution"), max_length=50, blank=True)
    # birth_date = models.DateField(null=True, blank=True)
    email_confirmed = models.BooleanField(_("email confirmed"), default=False)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # enroll user in courses that have 'auto_enroll' enabled
        courses = Course.objects.filter(auto_enroll=True)
        for course in courses:
            course.members.add(instance)
            course.learners.add(instance)



@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
