Changes
=======

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
