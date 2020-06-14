from django import template

register = template.Library()


@register.filter
def check_attribute(element, attribute):
    """
    Checks if element has attribute and return a boolean
    """

    return bool(hasattr(element, str(attribute)))

    # the return is a simplified version of the following code:
    # if hasattr(element, str(attribute)):
    #     return True
    # else:
    #     return False
