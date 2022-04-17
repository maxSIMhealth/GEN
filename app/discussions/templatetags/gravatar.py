import hashlib
from urllib.parse import urlencode

from django import template

register = template.Library()


@register.filter
def gravatar(user):
    email = user.email.lower().encode("utf-8")
    default = "robohash"
    size = 256
    forcedefault = "y"
    url = "https://www.gravatar.com/avatar/{md5}?{params}".format(
        md5=hashlib.md5(email).hexdigest(),
        params=urlencode({"d": default, "s": str(size), "forcedefault": forcedefault}),
    )
    return url
