Utils
=====


clean_duplicate_history
-----------------------

For performance reasons, ``django-simple-history`` always creates an ``HistoricalRecord``
when ``Model.save()`` is called regardless of data having actually changed.
If you find yourself with a lot of history duplicates you can schedule the
``clean_duplicate_history`` command

.. code-block:: bash

    $ python manage.py clean_duplicate_history --auto

You can use ``--auto`` to clean up duplicates for every model
with ``HistoricalRecords`` or enumerate specific models as args.
There is also ``-m/--minutes`` to specify how many minutes to go
back in history while searching (default checks whole history),
so you can schedule, for instance, an hourly cronjob such as

.. code-block:: bash

    $ python manage.py clean_duplicate_history -m 60 --auto

You can also use ``--excluded_fields`` to provide a list of fields to be excluded
from the duplicate check

.. code-block:: bash

    $ python manage.py clean_duplicate_history --auto --excluded_fields field1 field2

clean_old_history
-----------------------

You may want to remove historical records that have existed for a certain amount of time. 

If you find yourself with a lot of old history you can schedule the
``clean_old_history`` command

.. code-block:: bash

    $ python manage.py clean_old_history --auto

You can use ``--auto`` to remove old historial entries 
with ``HistoricalRecords`` or enumerate specific models as args.
You may also specify a  ``--days`` parameter, which indicates how many 
days of records you want to keep. The default it 30 days, meaning that
all records older than 30 days would be removed.

.. code-block:: bash

    $ python manage.py clean_old_history --days 60 --auto
