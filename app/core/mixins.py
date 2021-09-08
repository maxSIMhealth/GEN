from django.contrib.auth.mixins import AccessMixin

from courses.models import SectionItem, Course, Section


class BlockPeersAccessMixin(AccessMixin):
    """
    CBV mixin that blocks regular users/peers from accessing a page (course, section, or section item).
    It allows access to: author, instructor, editor, admin/staff.
    """
    def dispatch(self, request, *args, **kwargs):
        # defines objects based on type (section item, section, or course)
        if 'sectionitem_pk' in kwargs:
            restricted_object = SectionItem.objects.get(pk=self.kwargs['sectionitem_pk'])
            course_object = restricted_object.section.course
        elif 'section_pk' in kwargs:
            restricted_object = Section.objects.get(pk=self.kwargs['section_pk'])
            course_object = restricted_object.course
        else:
            restricted_object = Course.objects.get(pk=self.kwargs['pk'])
            course_object = restricted_object

        # initialize empty array
        allow_access = []

        # check if user is author/owner
        if not restricted_object.author == self.request.user:
            allow_access.append(False)
        else:
            allow_access.append(True)
        # check if user is admin or staff
        if not self.request.user.is_superuser or not self.request.user.is_staff:
            allow_access.append(False)
        else:
            allow_access.append(True)
        # check if user is course editor
        if not self.request.user in course_object.editors.all():
            allow_access.append(False)
        else:
            allow_access.append(True)

        # allow access if ANY of the conditions above is true
        if True in allow_access:
            return super().dispatch(request, *args, **kwargs)

        return self.handle_no_permission()