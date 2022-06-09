from django import template
from django.shortcuts import get_object_or_404

register = template.Library()


@register.simple_tag
def get_scorm_registration_details(learner, scorm_object):
    """
    Obtains Scorm Registration for a specific learner and SCORM package,
    which includes activity completion, attempts, score, etc.

    Args:
        learner: User (object).
        scorm_object: GEN ScormPackage (object).

    Returns: GEN ScormRegistration (object).

    """

    from scorm.models import ScormRegistration

    registration_details = get_object_or_404(
        ScormRegistration, package_object=scorm_object, learner=learner
    )

    return registration_details
