Introduction
============

django-workflows provides a generic workflow engine for Django.

Documentation
=============

For more documentation please visit: http://packages.python.org/django-workflows/

Code
====

The code can be found on github: http://github.com/diefenbach/django-workflows

Implementations
===============

If you want to see a comprehensive implementation of django-workflows take
a look at the CMS `LFC <http://pypi.python.org/pypi/django-lfc>`_

Changes
=======

1.1.1 (2014-06-26)
------------------

* Pins version for django-permissions to 1.1

1.1 (2014-06-25)
----------------

* Cleanup and performance improvements

1.0 (2010-08-24)
----------------

* First final release

1.0 beta 4 (2010-07-23)
-----------------------

* Changed: State.get_allowed_transitions: try to use the object's has_permissions
  method before using the one from the utils

1.0 beta 3 (2010-07-07)
-----------------------

* Bugfix utils.get_allowed_transitions; issue #2
* Bugfix: get_workflow_for_object method; issue #3

1.0 beta 2 (2010-05-19)
------------------------

* Bugfix: get_allowed_transitions; return only allowed permissions; issue #2.
* Added license

1.0 beta 1 (2010-05-17)
------------------------

* First beta release.

1.0 alpha 4 (2010-04-16)
------------------------

* Added get_initial_state method
* Moved WorkflowBase to __init__.py
* Added related_name for permissions to WorkflowPermissionRelation

1.0 alpha 3 (2010-03-22)
------------------------

* Changes according to `django-permissions <http://pypi.python.org/pypi/django-permissions>`_
  1.0a3 (Added roles)

1.0 alpha 2 (2010-03-22)
------------------------

* A lot of improvements

1.0 alpha 1 (2010-03-13)
------------------------

* Initial public release
