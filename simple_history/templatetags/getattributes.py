from django import template

register = template.Library()


def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""

    if hasattr(value, str(arg)):
        return getattr(value, arg)

register.filter('getattribute', getattribute)
