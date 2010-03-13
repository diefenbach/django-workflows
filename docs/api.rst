=====
Utils
=====

.. warning::

    django-workflows is in alpha state. Please consider the API as supposed 
    to be changed until it reaches beta state.

.. autofunction:: workflows.utils.set_workflow
.. autofunction:: workflows.utils.set_workflow_for_object
.. autofunction:: workflows.utils.get_workflow_for_model

.. autofunction:: workflows.utils.get_state
.. autofunction:: workflows.utils.set_state

.. autofunction:: workflows.utils.get_allowed_transitions

=======
Classes
=======

.. warning::

    django-workflows is in alpha state. Please consider the API as supposed 
    to be changed until it reaches beta state.

.. autoclass:: workflows.models.Workflow

.. autoclass:: workflows.models.State
    :members:
    
.. autoclass:: workflows.models.Transition

.. autoclass:: workflows.models.StateObjectRelation

.. autoclass:: workflows.models.WorkflowPermissionRelation

.. autoclass:: workflows.models.StatePermissionRelation
