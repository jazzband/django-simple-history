Advanced Usage
==============

Version-controlling with South
------------------------------

By default, Historical models live in the same app as the model they track.
Historical models are tracked by South in the same way as any other model.
Whenever the original model changes, the historical model will change also.

Therefore tracking historical models with South should work automatically.


History for Third-Party Model
-----------------------------

To track history for a model you didn't create, use the
``simple_history.register`` utility.  You can use this to track models from
third-party apps you don't have control over.  Here's an example of using
``simple_history.register`` to history-track the ``User`` model from the
``django.contrib.auth`` app:

.. code-block:: python

    from simple_history import register
    from django.contrib.auth.models import User

    register(User)
