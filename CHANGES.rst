Changes
=======

Unreleased
----------
- Removed support for Django versions prior to 2.2 (gh-652)
- Migrate from TravisCI to Github Actions (gh-739)
- Add Python 3.9 support (gh-745)

2.12.0 (2020-10-14)
-------------------
- Add default date to ``bulk_create_with_history`` and ``bulk_update_with_history`` (gh-687)
- Exclude ManyToManyFields when using ``bulk_create_with_history`` (gh-699)
- Added ``--excluded_fields`` argument to ``clean_duplicate_history`` command (gh-674)
- Exclude ManyToManyFields when fetching excluded fields (gh-707)
- Use default model manager for ``bulk_create_with_history`` and
  ``bulk_update_with_history`` instead of ``objects`` (gh-703)
- Add optional ``manager`` argument to ``bulk_update_with_history`` to use instead of
  the default manager (gh-703)
- Add support for Django 3.1 (gh-713)
- Fix a bug with ``clean_old_history`` command's `--days` argument (gh-722)

\* NOTE: This will be the last minor release before 3.0.0.

2.11.0 (2020-06-20)
-------------------
- Added ``clean_old_history`` management command (gh-675)
- Added ``user_db_constraint`` param to history to avoid circular reference on delete (gh-676)
- Leverages ``get_user`` from ``HistoricalRecords`` in order to set a fallback user on
  bulk update and bulk create (gh-677)

2.10.0 (2020-04-27)
-------------------
- Added ``bulk_update_with_history`` utility function (gh-650)
- Add default user and default change reason to ``bulk_create_with_history`` and ``bulk_update_with_history`` (gh-653)
- Add french translation (gh-654)
- Start using ``_change_reason`` instead of ``changeReason`` to add change reasons to historical
  objects. ``changeReason`` is deprecated and will be removed in version ``3.0.0`` (gh-655)

2.9.0 (2020-04-23)
------------------
- Add simple filtering if provided a minutes argument in ``clean_duplicate_history`` (gh-606)
- Add setting to convert ``FileField`` to ``CharField`` instead of ``TextField`` (gh-625)
- Added notes on BitBucket Pipelines (gh-627)
- import model ``ContentType`` in ``SimpleHistoryAdmin`` using ``django_apps.get_model``
  to avoid possible ``AppRegistryNotReady`` exception (gh-630)
- Fix ``utils.update_change_reason`` when user specifies excluded_fields (gh-637)
- Changed how ``now`` is imported from ``timezone`` (``timezone`` module is imported now) (gh-643)
- ``settings.SIMPLE_HISTORY_REVERT_DISABLED`` if True removes the Revert
  button from the history form for all historical models (gh-632))

2.8.0 (2019-12-02)
------------------
- Fixed ``bulk_create_with_history support`` for HistoryRecords with ``relation_name`` attribute (gh-591)
- Added support for ``bulk_create_with_history`` for databases different from PostgreSQL (gh-577)
- Fixed ``DoesNotExist`` error when trying to get instance if object is deleted (gh-571)
- Fix ``model_to_dict`` to detect changes in a parent model when using
  ``inherit=True`` (backwards-incompatible for users who were directly
  using previous version) (gh-576)
- Use an iterator for ``clean_duplicate_history`` (gh-604)
- Add support for Python 3.8 and Django 3.0 (gh-610)

2.7.3 (2019-07-15)
------------------
- Fixed ``BigAutoField`` not mirrored as ``BigInt`` (gh-556)
- Fixed ``most_recent()`` bug with ``excluded_fields`` (gh-561)
- Added official Django 2.2 support (gh-555)

2.7.2 (2019-04-17)
------------------
- Fixed ModuleNotFound issue for ``six`` (gh-553)

2.7.1 (2019-04-16)
------------------
- Added the possibility to create a relation to the original model (gh-536)
- Fix router backward-compatibility issue with 2.7.0 (gh-539, gh-547)
- Fix hardcoded history manager (gh-542)
- Replace deprecated ``django.utils.six`` with ``six`` (gh-526)
- Allow ``custom_model_name`` parameter to be a callable (gh-489)

2.7.0 (2019-01-16)
------------------
- \* Add support for ``using`` chained manager method and save/delete keyword argument (gh-507)
- Added management command ``clean_duplicate_history`` to remove duplicate history entries (gh-483)
- Updated most_recent to work with excluded_fields (gh-477)
- Fixed bug that prevented self-referential foreign key from using ``'self'`` (gh-513)
- Added ability to track custom user with explicit custom ``history_user_id_field`` (gh-511)
- Don't resolve relationships for history objects (gh-479)
- Reorganization of docs (gh-510)

\* NOTE: This change was not backward compatible for users using routers to write
history tables to a separate database from their base tables. This issue is fixed in
2.7.1.

2.6.0 (2018-12-12)
------------------
- Add ``app`` parameter to the constructor of ``HistoricalRecords`` (gh-486)
- Add ``custom_model_name`` parameter to the constructor of ``HistoricalRecords`` (gh-451)
- Fix header on history pages when custom site_header is used (gh-448)
- Modify ``pre_create_historical_record`` to pass ``history_instance`` for ease of customization (gh-421)
- Raise warning if ``HistoricalRecords(inherit=False)`` is in an abstract model (gh-341)
- Ensure custom arguments for fields are included in historical models' fields (gh-431)
- Add german translations (gh-484)
- Add ``extra_context`` parameter to history_form_view (gh-467)
- Fixed bug that prevented ``next_record`` and ``prev_record`` to work with custom manager names (gh-501)

2.5.1 (2018-10-19)
------------------
- Add ``'+'`` as the ``history_type`` for each instance in ``bulk_history_create`` (gh-449)
- Add support for  ``history_change_reason`` for each instance in ``bulk_history_create`` (gh-449)
- Add ``history_change_reason`` in the history list view under the  ``Change reason`` display name (gh-458)
- Fix bug that caused failures when using a custom user model (gh-459)

2.5.0 (2018-10-18)
------------------
- Add ability to cascade delete historical records when master record is deleted (gh-440)
- Added Russian localization (gh-441)

2.4.0 (2018-09-20)
------------------
- Add pre and post create_historical_record signals (gh-426)
- Remove support for ``django_mongodb_engine`` when converting AutoFields (gh-432)
- Add support for Django 2.1 (gh-418)

2.3.0 (2018-07-19)
------------------
- Add ability to diff ``HistoricalRecords`` (gh-244)

2.2.0 (2018-07-02)
------------------
- Add ability to specify alternative user_model for tracking (gh-371)
- Add util function ``bulk_create_with_history`` to allow bulk_create with history saved (gh-412)

2.1.1 (2018-06-15)
------------------
- Fixed out-of-memory exception when running populate_history management command (gh-408)
- Fix TypeError on populate_history if excluded_fields are specified (gh-410)

2.1.0 (2018-06-04)
------------------
- Add ability to specify custom ``history_reason`` field (gh-379)
- Add ability to specify custom ``history_id`` field (gh-368)
- Add HistoricalRecord instance properties ``prev_record`` and ``next_record`` (gh-365)
- Can set admin methods as attributes on object history change list template (gh-390)
- Fixed compatibility of >= 2.0 versions with old-style middleware (gh-369)

2.0 (2018-04-05)
----------------
- Added Django 2.0 support (gh-330)
- Dropped support for Django<=1.10 (gh-356)
- Fix bug where ``history_view`` ignored user permissions (gh-361)
- Fixed ``HistoryRequestMiddleware`` which hadn't been working for Django>1.9 (gh-364)

1.9.1 (2018-03-30)
------------------
- Use ``get_queryset`` rather ``than model.objects`` in ``history_view``. (gh-303)
- Change ugettext calls in models.py to ugettext_lazy
- Resolve issue where model references itself (gh-278)
- Fix issue with tracking an inherited model (abstract class) (gh-269)
- Fix history detail view on django-admin for abstract models (gh-308)
- Dropped support for Django<=1.6 and Python 3.3 (gh-292)

1.9.0 (2017-06-11)
------------------
- Add ``--batchsize`` option to the ``populate_history`` management command. (gh-231)
- Add ability to show specific attributes in admin history list view. (gh-256)
- Add Brazilian Portuguese translation file. (gh-279)
- Fix locale file packaging issue. (gh-280)
- Add ability to specify reason for history change. (gh-275)
- Test against Django 1.11 and Python 3.6. (gh-276)
- Add ``excluded_fields`` option to exclude fields from history. (gh-274)

1.8.2 (2017-01-19)
------------------
- Add Polish locale.
- Add Django 1.10 support.

1.8.1 (2016-03-19)
------------------
- Clear the threadlocal request object when processing the response to prevent test interactions. (gh-213)

1.8.0 (2016-02-02)
------------------
- History tracking can be inherited by passing ``inherit=True``. (gh-63)

1.7.0 (2015-12-02)
------------------
- Add ability to list history in admin when the object instance is deleted. (gh-72)
- Add ability to change history through the admin. (Enabled with the ``SIMPLE_HISTORY_EDIT`` setting.)
- Add Django 1.9 support.
- Support for custom tables names. (gh-196)

1.6.3 (2015-07-30)
------------------
- Respect ``to_field`` and ``db_column`` parameters (gh-182)

1.6.2 (2015-07-04)
------------------
- Use app loading system and fix deprecation warnings on Django 1.8 (gh-172)
- Update Landscape configuration

1.6.1 (2015-04-21)
------------------
- Fix OneToOneField transformation for historical models (gh-166)
- Disable cascading deletes from related models to historical models
- Fix restoring historical instances with missing one-to-one relations (gh-162)

1.6.0 (2015-04-16)
------------------
- Add support for Django 1.8+
- Deprecated use of ``CustomForeignKeyField`` (to be removed)
- Remove default reverse accessor to ``auth.User`` for historical models (gh-121)

1.5.4 (2015-01-03)
------------------
- Fix a bug when models have a ``ForeignKey`` with ``primary_key=True``
- Do NOT delete the history elements when a user is deleted.
- Add support for ``latest``
- Allow setting a reason for change. [using option changeReason]

1.5.3 (2014-11-18)
------------------
- Fix migrations while using ``order_with_respsect_to`` (gh-140)
- Fix migrations using south
- Allow history accessor class to be overridden in ``register()``

1.5.2 (2014-10-15)
------------------
- Additional fix for migrations (gh-128)

1.5.1 (2014-10-13)
------------------
- Removed some incompatibilities with non-default admin sites (gh-92)
- Fixed error caused by ``HistoryRequestMiddleware`` during anonymous requests (gh-115 fixes gh-114)
- Added workaround for clashing related historical accessors on User (gh-121)
- Added support for MongoDB AutoField (gh-125)
- Fixed CustomForeignKeyField errors with 1.7 migrations (gh-126 fixes gh-124)

1.5.0 (2014-08-17)
------------------
- Extended availability of the ``as_of`` method to models as well as instances.
- Allow ``history_user`` on historical objects to be set by middleware.
- Fixed error that occurs when a foreign key is designated using just the name of the model.
- Drop Django 1.3 support

1.4.0 (2014-06-29)
------------------
- Fixed error that occurs when models have a foreign key pointing to a one to one field.
- Fix bug when model verbose_name uses unicode (gh-76)
- Allow non-integer foreign keys
- Allow foreign keys referencing the name of the model as a string
- Added the ability to specify a custom ``history_date``
- Note that ``simple_history`` should be added to ``INSTALLED_APPS`` (gh-94 fixes gh-69)
- Properly handle primary key escaping in admin URLs (gh-96 fixes gh-81)
- Add support for new app loading (Django 1.7+)
- Allow specifying custom base classes for historical models (gh-98)

1.3.0 (2013-05-17)
------------------

- Fixed bug when using ``django-simple-history`` on nested models package
- Allow history table to be formatted correctly with ``django-admin-bootstrap``
- Disallow calling ``simple_history.register`` twice on the same model
- Added Python 3 support
- Added support for custom user model (Django 1.5+)

1.2.3 (2013-04-22)
------------------

- Fixed packaging bug: added admin template files to PyPI package

1.2.1 (2013-04-22)
------------------

- Added tests
- Added history view/revert feature in admin interface
- Various fixes and improvements

Oct 22, 2010
------------

- Merged setup.py from Klaas van Schelven - Thanks!

Feb 21, 2010
------------

- Initial project creation, with changes to support ForeignKey relations.
