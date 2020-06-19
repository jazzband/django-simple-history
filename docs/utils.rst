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


clean_old_history
-----------------------

You may want to remove historical records that have existed for a certain amount of time. 

If you find yourself with a lot of old history you can schedule the
``clean_old_history`` command

.. code-block:: bash

    $ python manage.py clean_old_history --auto

You can use ``--auto`` to clean up duplicates for every model
with ``HistoricalRecords`` or enumerate specific models as args.
There is also ``--days`` to specify how days you want to keep the records
back in history while searching (default is 30 days),
so you can schedule, for instance, an hourly cronjob such as

.. code-block:: bash

    $ python manage.py clean_old_history --days 60 --auto
