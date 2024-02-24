import warnings

from django import template

register = template.Library()


@register.inclusion_tag("simple_history/object_history_list.html", takes_context=True)
def display_list(context):
    warnings.warn(
        "'include' the context variable 'object_history_list_template' instead."
        " This will be removed in version 3.8.",
        DeprecationWarning,
    )
    return context
