from scorm.models import ScormPackage, ScormRegistration

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from GEN.decorators import course_enrollment_check
from GEN.support_methods import enrollment_test


@login_required
@course_enrollment_check(enrollment_test)
def scorm_exit_redirect(request, pk, section_pk, scorm_object_pk):
    scorm_object = get_object_or_404(ScormPackage, pk=scorm_object_pk)
    learner = request.user
    scorm_registration_object = get_object_or_404(
        ScormRegistration, package_object=scorm_object, learner=learner
    )

    # update scorm registration activity details
    scorm_registration_object.update_details()

    # update learner's section status based on Scorm Registration data
    # section_object = get_object_or_404(Section, pk=section_pk)
    section_object = scorm_registration_object.package_object.section
    section_status = section_object.status.get(learner=learner)
    section_status.update()

    scorm_section_url = reverse("section", args=[pk, section_pk])

    return HttpResponseRedirect(scorm_section_url)
