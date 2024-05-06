History Diffing
===============

When you have two instances of the same historical model
(such as the ``HistoricalPoll`` example above),
you can perform a diff using the ``diff_against()`` method to see what changed.
This will return a ``ModelDelta`` object with the following attributes:

- ``old_record`` and ``new_record``: The old and new history records
- ``changed_fields``: A list of the names of all fields that were changed between
  ``old_record`` and ``new_record``, in alphabetical order
- ``changes``: A list of ``ModelChange`` objects - one for each field in
  ``changed_fields``, in the same order.
  These objects have the following attributes:

  - ``field``: The name of the changed field
    (this name is equal to the corresponding field in ``changed_fields``)
  - ``old`` and ``new``: The old and new values of the changed field

    - For many-to-many fields, these values will be lists of dicts from the through
      model field names to the primary keys of the through model's related objects.
      The lists are sorted by the value of the many-to-many related object.

This may be useful when you want to construct timelines and need to get only
the model modifications.

.. code-block:: python

    poll = Poll.objects.create(question="what's up?")
    poll.question = "what's up, man?"
    poll.save()

    new_record, old_record = poll.history.all()
    delta = new_record.diff_against(old_record)
    for change in delta.changes:
        print(f"'{change.field}' changed from '{change.old}' to '{change.new}'")

    # Output:
    # 'question' changed from 'what's up?' to 'what's up, man?'

``diff_against()`` also accepts the following additional arguments:

- ``excluded_fields`` and ``included_fields``: These can be used to either explicitly
  exclude or include fields from being diffed, respectively.
- ``foreign_keys_are_objs``:

  - If ``False`` (default): The diff will only contain the raw primary keys of any
    ``ForeignKey`` fields.
  - If ``True``: The diff will contain the actual related model objects instead of just
    the primary keys.
    Deleted related objects (both foreign key objects and many-to-many objects)
    will be instances of ``DeletedObject``, which only contain a ``model`` field with a
    reference to the deleted object's model, as well as a ``pk`` field with the value of
    the deleted object's primary key.

    Note that this will add extra database queries for each related field that's been
    changed - as long as the related objects have not been prefetched
    (using e.g. ``select_related()``).

  A couple examples showing the difference:

  .. code-block:: python

      # --- Effect on foreign key fields ---

      whats_up = Poll.objects.create(pk=15, name="what's up?")
      still_around = Poll.objects.create(pk=31, name="still around?")

      choice = Choice.objects.create(poll=whats_up)
      choice.poll = still_around
      choice.save()

      new, old = choice.history.all()

      default_delta = new.diff_against(old)
      # Printing the changes of `default_delta` will output:
      # 'poll' changed from '15' to '31'

      delta_with_objs = new.diff_against(old, foreign_keys_are_objs=True)
      # Printing the changes of `delta_with_objs` will output:
      # 'poll' changed from 'what's up?' to 'still around?'

      # Deleting all the polls:
      Poll.objects.all().delete()
      delta_with_objs = new.diff_against(old, foreign_keys_are_objs=True)
      # Printing the changes of `delta_with_objs` will now output:
      # 'poll' changed from 'Deleted poll (pk=15)' to 'Deleted poll (pk=31)'


      # --- Effect on many-to-many fields ---

      informal = Category.objects.create(pk=63, name="informal questions")
      whats_up.categories.add(informal)

      new = whats_up.history.latest()
      old = new.prev_record

      default_delta = new.diff_against(old)
      # Printing the changes of `default_delta` will output:
      # 'categories' changed from [] to [{'poll': 15, 'category': 63}]

      delta_with_objs = new.diff_against(old, foreign_keys_are_objs=True)
      # Printing the changes of `delta_with_objs` will output:
      # 'categories' changed from [] to [{'poll': <Poll: what's up?>, 'category': <Category: informal questions>}]

      # Deleting all the categories:
      Category.objects.all().delete()
      delta_with_objs = new.diff_against(old, foreign_keys_are_objs=True)
      # Printing the changes of `delta_with_objs` will now output:
      # 'categories' changed from [] to [{'poll': <Poll: what's up?>, 'category': DeletedObject(model=<class 'models.Category'>, pk=63)}]
