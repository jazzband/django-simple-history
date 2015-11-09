from django import template

try:  # Django < 1.5
    from django.templatetags.future import url
except ImportError:
    from django.template.defaulttags import url

register = template.Library()

register.tag(url)
