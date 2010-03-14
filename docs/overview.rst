========
Overview
========

Permissions
-----------

django-workflows comes with `django-permissions 
<http://packages.python.org/django-permissions/>`_, which is a per-object 
permission framework for Django.

Every object can have specific permissions for specific groups. Every user 
has all permissions from the groups he is member of.

See `django-permissions <http://packages.python.org/django-permissions/>`_
for more.

Workflows
---------

A workflow consists of a sequence of connected (through transitions) states. 
The transitions can be restricted by permissions.

A workflow can be assigned to models and model instances. All instances will
"inherit" the workflow of its model. If an instance has an own workflow this 
will have precedence. In this way all instances of a content type have the 
same workflow unless a specific instance of that content type have an other 
workflow assigned.

Every workflow manages a set of permissions. Every workflow state can grant
or remove this permissions from the instance for several groups. In this way
objects have different permissions per workflow state.