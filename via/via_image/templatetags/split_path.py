from django import template
from django.template.defaultfilters import stringfilter


register = template.Library()

@stringfilter
@register.filter
def split(url):
    name = url.rsplit('/', 1)[-1]
    return name

# register.filter('split', split)