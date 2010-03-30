=====
Utils
=====

.. warning::

    django-workflows is in alpha state. Please consider the API as supposed 
    to be changed until it reaches beta state.

Workflow
--------
.. autofunction:: workflows.utils.set_workflow
.. autofunction:: workflows.utils.set_workflow_for_object
.. autofunction:: workflows.utils.set_workflow_for_model

.. autofunction:: workflows.utils.remove_workflow
.. autofunction:: workflows.utils.remove_workflow_from_object
.. autofunction:: workflows.utils.remove_workflow_from_model

.. autofunction:: workflows.utils.get_workflow
.. autofunction:: workflows.utils.get_workflow_for_object
.. autofunction:: workflows.utils.get_workflow_for_model

.. autofunction:: workflows.utils.get_objects_for_workflow

States
------
.. autofunction:: workflows.utils.get_state
.. autofunction:: workflows.utils.set_state
.. autofunction:: workflows.utils.set_initial_state

Transitions
-----------
.. autofunction:: workflows.utils.get_allowed_transitions
.. autofunction:: workflows.utils.do_transition

Permissions
-----------
.. autofunction:: workflows.utils.update_permissions

=======
Classes
=======

.. warning::

    django-workflows is in alpha state. Please consider the API as supposed 
    to be changed until it reaches beta state.

.. autoclass:: workflows.models.WorkflowBase
    :members:

.. autoclass:: workflows.models.Workflow
    :members:

.. autoclass:: workflows.models.State
    :members:
    
.. autoclass:: workflows.models.Transition
    :members:
    
.. autoclass:: workflows.models.StateObjectRelation
    :members:
    
.. autoclass:: workflows.models.WorkflowPermissionRelation
    :members:
    
.. autoclass:: workflows.models.StatePermissionRelation
    :members: