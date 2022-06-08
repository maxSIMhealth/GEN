from scorm.support_methods import generate_launch_url

from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def generate_scorm_object_url(context, learner, scorm_object):
    """
    Obtain and return the ScormCloud URL that allows the learner to access the SCORM package.

    Args:
        context: Page context (object).
        learner: User (object).
        scorm_object: ScormPackage (object).

    Returns: URL (string).

    """

    request = context["request"]
    section_url = reverse(
        "scorm_exit_redirect",
        args=[scorm_object.section.course.pk, scorm_object.section.pk, scorm_object.pk],
    )

    # the URL that will be opened after closing/exiting the ScormCloud page
    redirect_on_exit_url = request.build_absolute_uri(section_url)

    # generate a ScormCloud url specific for the current participant
    url = generate_launch_url(
        scorm_object, learner, redirect_on_exit_url=redirect_on_exit_url
    )

    return url
