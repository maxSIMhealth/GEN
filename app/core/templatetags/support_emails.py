from django import template
from django.conf import settings as django_settings

register = template.Library()


@register.inclusion_tag("tags/support_emails.html")
def support_emails():
    support_emails_list = django_settings.SUPPORT_EMAILS

    return {"support_emails": support_emails_list}
