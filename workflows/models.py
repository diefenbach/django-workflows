from django.db import models

# django imports
from django.contrib.auth.models import Group
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# permissions imports
from permissions.models import Permission

class Workflow(models.Model):
    """A workflow consists of a sequence of connected (through transitions)
    states. It can be assigned to a model and / or model instances.

    **Attributes:**

    model
        The model the workflow belongs to. Can be any 

    content
        The object the workflow belongs to.

    name
        The unique name of the workflow.

    states
        The states of the workflow.

    initial_state
        The initial state the model / content gets if created.

    """
    name = models.CharField(_(u"Name"), max_length=100, unique=True)
    initial_state = models.ForeignKey("State", related_name="workflow_state", blank=True, null=True)

    def __unicode__(self):
        return self.name

class State(models.Model):
    """A certain state within workflow.

    **Attributes:**

    name
        The unique name of the state within the workflow.

    workflow
        The workflow to which the state belongs.

    transitions
        The transitions of a workflow state.

    """
    name = models.CharField(_(u"Name"), max_length=100)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"), related_name="states")
    transitions = models.ManyToManyField("Transition", verbose_name=_(u"Transitions"), blank=True, null=True, related_name="states")

    def __unicode__(self):
        return self.name

    def get_allowed_transitions(self, user):
        """Returns all allowed transitions for given user.
        """
        return self.transitions.all()

class Transition(models.Model):
    """A transition from a source to a destination state. The transition can
    be used from several source states.

    **Attributes:**

    name
        The unique name of the transition within a workflow.

    workflow
        The workflow to which the transition belongs. Must be a Workflow 
        instance.

    destination
        The state after a transition has been processed. Must be a State 
        instance.

    condition
        The condition when the transition is available. Can be any python 
        expression.

    permission
        The necessary permission to process the transition. Must be a
        Permission instance.

    """
    name = models.CharField(_(u"Name"), max_length=100)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"))
    destination = models.ForeignKey(State, verbose_name=_(u"Destination"), related_name="destination_state")
    condition = models.CharField(_(u"Condition"), blank=True, max_length=100)
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"), blank=True, null=True)

    def __unicode__(self):
        return self.name

class StateObjectRelation(models.Model):
    """Stores the workflow state of an object.

    **Attributes:**

    content
        The object for which the state is stored. This can be any instance of
        a Django model.

    state
        The state of content. This must be a State instance.
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="state_object", blank=True, null=True)
    content_id = models.PositiveIntegerField(_(u"Content id"), blank=True, null=True)
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    state = models.ForeignKey(State, verbose_name = _(u"State"))

    def __unicode__(self):
        return "%s %s - %s" % (self.content_type.name, self.content_id, self.state.name)

    class Meta:
        unique_together = ("content_type", "content_id", "state")

class WorkflowObjectRelation(models.Model):
    """Stores an workflow of an object.

    **Attributes:**

    content
        The object for which the workflow is stored. This can be any instance of
        a Django model.

    workflow
        The workflow which is assigned to an object. This needs to be a workflow
        instance.
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="workflow_object", blank=True, null=True)
    content_id = models.PositiveIntegerField(_(u"Content id"), blank=True, null=True)
    content = generic.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"))

    class Meta:
        unique_together = ("content_type", "content_id")

    def __unicode__(self):
        return "%s %s - %s" % (self.content_type.name, self.content_id, self.workflow.name)

class WorkflowModelRelation(models.Model):
    """Stores an workflow for a model (ContentType).

    **Attributes:**

    Content Type
        The content type for which the workflow is stored. This can be any
        instance of a Django model.

    workflow
        The workflow which is assigned to an object. This needs to be a
        workflow instance.
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content Type"), unique=True)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"))

    def __unicode__(self):
        return "%s - %s" % (self.content_type.name, self.workflow.name)

# Permissions relation #######################################################

class WorkflowPermissionRelation(models.Model):
    """Stores the permissions for which a workflow is responsible.

    **Attributes:**

    workflow
        The workflow which is responsible for the permissions. Needs to be a
        Workflow instance.
    permission
        The permission for which the workflow is responsible. Needs to be a
        Permission instance.
    """
    workflow = models.ForeignKey(Workflow)
    permission = models.ForeignKey(Permission)

    def __unicode__(self):
        return "%s %s" % (self.workflow.name, self.permission.name)

class StatePermissionRelation(models.Model):
    """Stores granted permission for state and group.

    **Attributes:**

    state
        The state for which the group has the permission. Needs to be a State
        instance.
    permission
        The permission for which the workflow is responsible. Needs to be a
        Permission instance.
    group
        The group for which the state has the permission. Needs to be a Django
        Group instance.
    """
    state = models.ForeignKey(State, verbose_name=_(u"State"))
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))
    group = models.ForeignKey(Group, verbose_name=_(u"Group"))

    def __unicode__(self):
        return "%s %s %s" % (self.state.name, self.group.name, self.permission.name)