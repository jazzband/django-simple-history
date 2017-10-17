"""
django-simple-history exceptions and warnings classes.
"""


class MultipleRegistrationsError(Exception):
    """The model has been registered to have history tracking more than once"""
    pass
