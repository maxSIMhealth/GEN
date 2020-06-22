# original: https://stackoverflow.com/a/35568978/481690

from django import template

register = template.Library()


@register.filter(name="likert_range")
def _likert_range(_range, args=None):
    _min = _range.lower
    # incrementing max value by 1 to fit likert scale representation
    _max = _range.upper + 1
    return range(_min, _max)
