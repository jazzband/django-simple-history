Signals
------------------------------------
`django-simple-history` includes signals that help you provide custom behavior when
saving a historical record. Arguments passed to the signals include the following:

.. glossary::
    instance
        The source model instance being saved

    history_instance
        The corresponding history record

    history_date
        Datetime of the history record's creation

    history_change_reason
        Freetext description of the reason for the change

    history_user
        The user that instigated the change

    using
        The database alias being used

To connect the signals to your callbacks, you can use the ``@receiver`` decorator:

.. code-block:: python

    from django.dispatch import receiver
    from simple_history.signals import (
        pre_create_historical_record,
        post_create_historical_record
    )

    @receiver(pre_create_historical_record)
    def pre_create_historical_record_callback(sender, **kwargs):
        print("Sent before saving historical record")

    @receiver(post_create_historical_record)
    def post_create_historical_record_callback(sender, **kwargs):
        print("Sent after saving historical record")
