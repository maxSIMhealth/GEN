from django import template

from core.models import FooterLogoFile

register = template.Library()


@register.inclusion_tag("partials/footer_logos.html", takes_context=False)
def footer_logos():
    logos = FooterLogoFile.objects.all()

    return {
        "footer_logos": logos
    }