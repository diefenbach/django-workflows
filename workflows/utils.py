# django imports
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError

# workflows imports
from workflows.models import WorkflowObjectRelation
from workflows.models import WorkflowModelRelation
from workflows.models import StateObjectRelation
from workflows.models import StatePermissionRelation
from workflows.models import WorkflowPermissionRelation

# permissions imports
import permissions.utils

def set_workflow(workflow, ctype_or_obj):
    """Sets the workflow for passed content type or object. See the specific
    methods for more information.

    **Parameters:**

    workflow
        The workflow which should be set to the object or model.
    ctype_or_obj
        The content type or the object to which the passed workflow should be
        set. Can be either a ContentType instance or any Django model
        instance.
    """
    if isinstance(ctype_or_obj, ContentType):
        return set_workflow_for_model(workflow, ctype_or_obj)
    else:
        return set_workflow_for_object(workflow, ctype_or_obj)

def set_workflow_for_object(workflow, obj):
    """Sets the passed workflow to the passed object.

    If the object has already the given workflow nothing happens. Otherwise
    the object gets the passed workflow and the state is set to the workflow's
    initial state.

    **Parameters:**

    workflow
        The workflow which should be set to the object.
    obj
        The object which gets the passed workflow.
    """
    ctype = ContentType.objects.get_for_model(obj)
    try:
        wor = WorkflowObjectRelation.objects.get(content_type=ctype, content_id=obj.id)
    except WorkflowObjectRelation.DoesNotExist:
        WorkflowObjectRelation.objects.create(content = obj, workflow=workflow)
        set_state(obj, workflow.initial_state)
    else:
        if wor.workflow != workflow:
            wor.workflow = workflow
            wor.save()
            set_state(obj, workflow.initial_state)

def set_workflow_for_model(workflow, ctype):
    """Sets the passed workflow to the passed content type. If the content
    type has already an assigned workflow the workflow is overwritten.

    The objects which had the old workflow must updated explicitely.

    **Parameters:**

    workflow
        The workflow which should be set to passend content type. Must be a
        Workflow instance.
    ctype
        The content type to which the passed workflow should be assigned. Can
        be any Django model instance
    """
    try:
        wor = WorkflowModelRelation.objects.get(content_type=ctype)
    except WorkflowModelRelation.DoesNotExist:
        WorkflowModelRelation.objects.create(content_type=ctype, workflow=workflow)
    else:
        wor.workflow = workflow
        wor.save()

def get_workflow(obj):
    """Returns the workflow for the passed object. It takes it either from
    the passed object or - if the object doesn't have a workflow - from the
    passed object's ContentType.

    **Parameters:**

    object
        The object for which the workflow should be returend. Can be any
        Django model instance.
    """
    workflow = get_workflow_for_obj(obj)
    if workflow is not None:
        return workflow

    ctype = ContentType.objects.get_for_model(obj)
    return get_workflow_for_model(ctype)

def get_workflow_for_obj(obj):
    """Returns the workflow for the passed object.

    **Parameters:**

    obj
        The object for which the workflow should be returned. Can be any
        Django model instance.
    """
    try:
        wor = WorkflowObjectRelation.objects.get()
    except WorkflowObjectRelation.DoesNotExist:
        return None
    else:
        return wor.workflow

def get_workflow_for_model(ctype):
    """Returns the workflow for the passed model.

    **Parameters:**

    ctype
        The content type for which the workflow should be returned. Must be
        a Django ContentType instance.
    """
    try:
        wor = WorkflowModelRelation.objects.get(content_type=ctype)
    except WorkflowModelRelation.DoesNotExist:
        return None
    else:
        return wor.workflow

def get_state(obj):
    """Returns the current workflow state for the passed object.

    **Parameters:**

    obj
        The object for which the workflow state should be returned. Can be any
        Django model instance.
    """
    ctype = ContentType.objects.get_for_model(obj)
    try:
        sor = StateObjectRelation.objects.get(content_type=ctype, content_id=obj.id)
    except StateObjectRelation.DoesNotExist:
        return None
    else:
        return sor.state

def set_state(obj, state):
    """Sets the current state for the passed object and updates the
    permissions for the object.

    **Parameters:**

    obj
        The object for which the workflow state should be set. Can be any
        Django model instance.
    state
        The state which should be set to the passed object.
    """
    ctype = ContentType.objects.get_for_model(obj)
    try:
        sor = StateObjectRelation.objects.get(content_type=ctype, content_id=obj.id)
    except StateObjectRelation.DoesNotExist:
        sor = StateObjectRelation.objects.create(content=obj, state=state)
    else:
        sor.state = state
        sor.save()
    update_permissions(obj)

def get_allowed_transitions(user, obj):
    """Returns all allowed transitions for passed obj.
    """
    workflow = get_workflow(obj)

    transitions = workflow.transitions.all()

def update_permissions(obj):
    """Updates the permission of the object according to the object's current
       workflow state.
    """
    workflow = get_workflow(obj)
    state = get_state(obj)
    
    # Remove all permissions for the workflow
    for group in Group.objects.all():
        for wpr in WorkflowPermissionRelation.objects.filter(workflow=workflow):
            permissions.utils.remove_permission(wpr.permission, group, obj)
    
    # Grant permission for the state        
    for spr in StatePermissionRelation.objects.filter(state=state):
        permissions.utils.grant_permission(spr.permission, spr.group, obj)
