from django import template

register = template.Library()


@register.inclusion_tag("simple_history/_object_history_list.html",
                        takes_context=True)
def display_list(context, cl):
    print str(cl)
    context.update({'foo': str(cl)})
    return context
