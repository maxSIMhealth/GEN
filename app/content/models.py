from courses.models import SectionItem
from tinymce.models import HTMLField


class ContentItem(SectionItem):
    content = HTMLField(
        blank=True,
        null=True
    )
