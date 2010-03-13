=====
Usage
=====

.. warning::

    django-workflows is in alpha state. Please consider the API as supposed 
    to be changed until it reaches beta state.

Create a simple workflow
------------------------

.. code-block:: python
    
    # Create the workflow object
    >>> from workflows.models import Workflow
    >>> workflow = Workflow.objects.create(name="Standard")

    # Create the workflow states
    >>> from workflows.models import State
    >>> private = State.objects.create(name="Private", workflow= workflow)
    >>> public = State.objects.create(name="Public", workflow= workflow)

    # Create the workflow transitions
    >>> from workflows.models import Transition
    >>> make_public = Transition.objects.create(name="Make public", workflow=workflow, destination=public)
    >>> make_private = Transition.objects.create(name="Make private", workflow=workflow, destination=private)

    # Add the transitions to the states
    >>> private.transitions.add(make_public)
    >>> public.transitions.add(make_private)

    # Define the initial state
    >>> workflow.initial_state = private
    >>> workflow.save()

Your would now be ready to assign this workflow to an object, but first we 
want to add some permissions for which the workflow takes care of.

Add permissions
---------------

.. code-block:: python

    # Add a group
    >>> from django.contrib.auth.models import Group
    >>> from permissions.utils import register_group
    >>> owner = register_group("Owner")

    # Create a user
    >>> from django.contrib.auth.models import User
    >>> user = User.objects.create(username="john")

    # Assign user to group
    >>> user.groups.add(owner)

    # Create example content type
    >>> from django.contrib.flatpages.models import FlatPage
    >>> page_1 = FlatPage.objects.create(url="/page-1/", title="Page 1")

    # Register permissions
    >>> from permissions.utils import register_permission
    >>> view = register_permission("View", "view")
    >>> edit = register_permission("Edit", "edit")

    # Add all permissions which are managed by the workflow
    >>> from workflows.models import WorkflowPermissionRelation
    >>> wpr = WorkflowPermissionRelation.objects.create(workflow=workflow, permission=view)
    >>> wpr = WorkflowPermissionRelation.objects.create(workflow=workflow, permission=edit)

    # Add permissions for the single states
    >>> from workflows.models import StatePermissionRelation
    >>> spr = StatePermissionRelation.objects.create(state=public, permission=view, group=owner)
    >>> spr = StatePermissionRelation.objects.create(state=private, permission=view, group=owner)
    >>> spr = StatePermissionRelation.objects.create(state=private, permission=edit, group=owner)
    
    # Assign the workflow to the content object
    >>> from workflows.utils import set_workflow
    >>> set_workflow(workflow, page_1)

    # Now self.page_1 has the intial workflow state.
    >>> from permissions.utils import has_permission
    >>> has_permission("edit", user, page_1)
    True
    
    # Now we change the workflow state
    >>> set_state(self.page_1, self.public)
    >>> has_permission("edit", user, page_1)
    False
