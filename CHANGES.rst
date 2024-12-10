Changes
=======

Unreleased
----------

- Made ``skip_history_when_saving`` work when creating an object - not just when
  updating an object (gh-1262)
- Improved performance of the ``latest_of_each()`` history manager method (gh-1360)
- Fixed issue with deferred fields causing DoesNotExist error (gh-678)
- Added HistoricOneToOneField (gh-1394)
- Updated all djangoproject.com links to reference the stable version (gh-1420)
- Dropped support for Python 3.8, which reached end-of-life on 2024-10-07 (gh-1421)
- Added support for Django 5.1 (gh-1388)
- Added pagination to ``SimpleHistoryAdmin`` (gh-1277)
- Fixed issue with history button not working when viewing historical entries in the
  admin (gh-527)
- Move repository to the Django Commons organization (gh-1391)

3.7.0 (2024-05-29)
------------------

- Dropped support for Django 3.2, which reached end-of-life on 2024-04-01 (gh-1344)
- Removed the temporary requirement on ``asgiref>=3.6`` added in 3.5.0,
  now that the minimum required Django version is 4.2 (gh-1344)
- Migrated package building from using the deprecated ``setup.py`` to using
  ``pyproject.toml`` (with Hatchling as build backend);
  ``setup.py`` has consequently been removed (gh-1348)
- Added ``django>=4.2`` as an installation dependency, to mirror the minimum version
  tested in our CI (gh-1349)

3.6.0 (2024-05-26)
------------------

- Support custom History ``Manager`` and ``QuerySet`` classes (gh-1280)
- Renamed the (previously internal) admin template
  ``simple_history/_object_history_list.html`` to
  ``simple_history/object_history_list.html``, and added the field
  ``SimpleHistoryAdmin.object_history_list_template`` for overriding it (gh-1128)
- Deprecated the undocumented template tag ``simple_history_admin_list.display_list()``;
  it will be removed in version 3.8 (gh-1128)
- Added ``SimpleHistoryAdmin.get_history_queryset()`` for overriding which ``QuerySet``
  is used to list the historical records (gh-1128)
- Added ``SimpleHistoryAdmin.get_history_list_display()`` which returns
  ``history_list_display`` by default, and made the latter into an actual field (gh-1128)
- ``ModelDelta`` and ``ModelChange`` (in ``simple_history.models``) are now immutable
  dataclasses; their signatures remain unchanged (gh-1128)
- ``ModelDelta``'s ``changes`` and ``changed_fields`` are now sorted alphabetically by
  field name. Also, if ``ModelChange`` is for an M2M field, its ``old`` and ``new``
  lists are sorted by the related object. This should help prevent flaky tests. (gh-1128)
- ``diff_against()`` has a new keyword argument, ``foreign_keys_are_objs``;
  see usage in the docs under "History Diffing" (gh-1128)
- Added a "Changes" column to ``SimpleHistoryAdmin``'s object history table, listing
  the changes between each historical record of the object; see the docs under
  "Customizing the History Admin Templates" for overriding its template context (gh-1128)
- Fixed the setting ``SIMPLE_HISTORY_ENABLED = False`` not preventing M2M historical
  records from being created (gh-1328)
- For history-tracked M2M fields, adding M2M objects (using ``add()`` or ``set()``)
  used to cause a number of database queries that scaled linearly with the number of
  objects; this has been fixed to now be a constant number of queries (gh-1333)

3.5.0 (2024-02-19)
------------------

- Fixed ``FieldError`` when creating historical records for many-to-many fields with
  ``to="self"`` (gh-1218)
- Allow ``HistoricalRecords.m2m_fields`` as str (gh-1243)
- Fixed ``HistoryRequestMiddleware`` deleting non-existent
  ``HistoricalRecords.context.request`` in very specific circumstances (gh-1256)
- Added ``custom_historical_attrs`` to ``bulk_create_with_history()`` and
  ``bulk_update_with_history()`` for setting additional fields on custom history models
  (gh-1248)
- Passing an empty list as the ``fields`` argument to ``bulk_update_with_history()`` is
  now allowed; history records will still be created (gh-1248)
- Added temporary requirement on ``asgiref>=3.6`` while the minimum required Django
  version is lower than 4.2 (gh-1261)
- Small performance optimization of the ``clean-duplicate_history`` command (gh-1015)
- Support Simplified Chinese translation (gh-1281)
- Added support for Django 5.0 (gh-1283)
- Added support for Python 3.13 (gh-1289)

3.4.0 (2023-08-18)
------------------

- Fixed typos in the docs
- Added feature to evaluate ``history`` model permissions explicitly when
  ``SIMPLE_HISTORY_ENFORCE_HISTORY_MODEL_PERMISSIONS`` is set to ``True``
  in ``settings`` (gh-1017).
- Fixed ``SimpleHistoryAdmin`` not properly integrating with custom user models (gh-1177)
- Support Indonesian translation (gh-1198)
- Support Urdu translation (gh-1199)
- Support Norwegian Bokmål translation (gh-1210)
- Dropped support for Python 3.7, which reached end-of-life on 2023-06-27 (gh-1202)
- Dropped support for Django 4.0, which reached end-of-life on 2023-04-01 (gh-1202)
- Added support for Django 4.2 (gh-1202)
- Made ``bulk_update_with_history()`` return the number of model rows updated (gh-1206)
- Fixed ``HistoryRequestMiddleware`` not cleaning up after itself (i.e. deleting
  ``HistoricalRecords.context.request``) under some circumstances (gh-1188)
- Made ``HistoryRequestMiddleware`` async-capable (gh-1209)
- Fixed error when setting ``table_name`` with ``inherit=True`` (gh-1195)

3.3.0 (2023-03-08)
------------------

- Made it possible to use the new ``m2m_fields`` with model inheritance (gh-1042)
- Added two signals: ``pre_create_historical_m2m_records`` and ``post_create_historical_m2m_records`` (gh-1042)
- Added ``tracked_fields`` attribute to historical models (gh-1038)
- Fixed ``KeyError`` when running ``clean_duplicate_history`` on models with ``excluded_fields`` (gh-1038)
- Added support for Python 3.11 (gh-1053)
- Added Arabic translations (gh-1056)
- Fixed a code example under "Tracking many to many relationships" (gh-1069)
- Added a ``--base-manager`` option to the ``clean_duplicate_history`` management command (gh-1115)

3.2.0 (2022-09-28)
------------------

- Fixed typos in the docs
- Removed n+1 query from ``bulk_create_with_history`` utility (gh-975)
- Started using ``exists`` query instead of ``count`` in ``populate_history`` command (gh-982)
- Add basic support for many-to-many fields (gh-399)
- Added support for Django 4.1 (gh-1021)

3.1.1 (2022-04-23)
------------------

Full list of changes:

- Fix py36 references in pyproject.toml (gh-960)
- Fix local setup.py install versioning issue (gh-960)
- Remove py2 universal wheel cfg - only py3 needed now (gh-960)


3.1.0 (2022-04-09)
------------------

Breaking Changes:

- Dropped support for Django 2.2 (gh-968)
- Dropped support for Django 3.1 (gh-952)
- Dropped support for Python 3.6, which reached end-of-life on 2021-12-23 (gh-946)

Upgrade Implications:

- Run `makemigrations` after upgrading to realize the benefit of indexing changes.

Full list of changes:

- Added queryset-based filtering with ``as_of`` (gh-397)
- Added index on `history_date` column; opt-out with setting `SIMPLE_HISTORY_DATE_INDEX` (gh-565)
- RecordModels now support a ``no_db_index`` setting, to drop indices in historical models,
  default stays the same (gh-720)
- Support ``included_fields`` for ``history.diff_against`` (gh-776)
- Improve performance of ``history.diff_against`` by reducing number of queries to 0 in most cases (gh-776)
- Fixed ``prev_record`` and ``next_record`` performance when using ``excluded_fields`` (gh-791)
- Fixed `update_change_reason` in pk (gh-806)
- Fixed bug where serializer of djangorestframework crashed if used with ``OrderingFilter`` (gh-821)
- Fixed `make format` so it works by using tox (gh-859)
- Fixed bug where latest() is not idempotent for identical ``history_date`` records (gh-861)
- Added ``excluded_field_kwargs`` to support custom ``OneToOneField`` that have
  additional arguments that don't exist on ``ForeignKey``. (gh-870)
- Added Czech translations (gh-885)
- Added ability to break into debugger on unit test failure (gh-890)
- Added pre-commit for better commit quality (gh-896)
- Russian translations update (gh-897)
- Added support for Django 4.0 (gh-898)
- Added Python 3.10 to test matrix (gh-899)
- Fix bug with ``history.diff_against`` with non-editable fields (gh-923)
- Added HistoricForeignKey (gh-940)
- Support change reason formula feature. Change reason formula can be defined by overriding
  ``get_change_reason_for_object`` method after subclassing ``HistoricalRecords`` (gh-962)


3.0.0 (2021-04-16)
------------------

Breaking changes:

- Removed support for Django 3.0
- Removed `changeReason` in favor of `_change_reason` (see 2.10.0)

Full list of changes:

- Removed support for Django versions prior to 2.2 (gh-652)
- Migrate from TravisCI to Github Actions (gh-739)
- Add Python 3.9 support (gh-745)
- Support ``ignore_conflicts`` in ``bulk_create_with_history`` (gh-733)
- Use ``asgiref`` when available instead of thread locals (gh-747)
- Sort imports with isort (gh-751)
- Queryset ``history.as_of`` speed improvements by calculating in the DB (gh-758)
- Increase `black` and `isort` python version to 3.6 (gh-817)
- Remove Django 3.0 support (gh-817)
- Add Django 3.2 support (gh-817)
- Improve French translations (gh-811)
- Remove support for changeReason (gh-819)

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
