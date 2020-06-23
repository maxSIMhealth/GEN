# original: https://stackoverflow.com/a/35568978/481690

from django import template

register = template.Library()


@register.filter(name="likert_range")
def _likert_range(_range, args=None):
    _min = _range.lower
    if _range.upper:
        # incrementing max value by 1 to fit likert scale representation
        _max = _range.upper + 1
        response = range(_min, _max)
    else:
        response = [_min]
    return response
