Changes
=======

tip (unreleased)
----------------
- Fixed error that occurs when models have a foreign key pointing to a one to one field.

- Allow non-integer foreign keys
- Allow foreign keys referencing the name of the model as a string

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
