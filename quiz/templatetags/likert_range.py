# original: https://stackoverflow.com/a/35568978/481690

from django import template

register = template.Library()


@register.filter(name='likert_range')
def _likert_range(_min, args=None):
    _max, _step = None, None
    if args:
        if not isinstance(args, int):
            _max, _step = map(int, args.split(','))
        else:
            _max = args
    # incrementing max value by 1 to fit likert scale representation
    args = filter(None, (_min, _max + 1, _step))
    return range(*args)
