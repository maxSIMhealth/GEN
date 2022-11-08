from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_socialapps_with_context(context):
    """
    Returns a list of social authentication providers for the current site.

    Usage: `{% get_socialapps_with_context as socialaccount_apps %}`.

    Then within the template context, `socialaccount_apps` will hold
    a list of social accounts configured for the current site.

    Note: openid accounts are not supported yet. Please check django-all source code
    for references.
    """
    from django.contrib.sites.models import Site

    request = context["request"]
    site = Site.objects.get_current(request)
    socialapps = site.socialapp_set.all()

    return socialapps
