from django.db import models

# django imports
from django.contrib.auth.models import Group
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

# permissions imports
from permissions.models import Permission

# workflows imports
import workflows.utils

class WorkflowBase(object):
    """Mixin class to make objects workflow aware.
    """
    def get_workflow(self):
        """Returns the current workflow of the object.
        """
        return workflows.utils.get_workflow(self)

    def remove_workflow(self):
        """Removes the workflow from the object. After this function has been
        called the object has no *own* workflow anymore (it might have one via
        its content type).

        """
        return workflows.utils.remove_workflow_from_object(self)

    def set_workflow(self, workflow):
        """Sets the passed workflow to the object. This will set the local
        workflow for the object.

        If the object has already the given workflow nothing happens.
        Otherwise the object gets the passed workflow and the state is set to
        the workflow's initial state.

        **Parameters:**

        workflow
            The workflow which should be set to the object. Can be a Workflow
            instance or a string with the workflow name.
        obj
            The object which gets the passed workflow.
        """
        return workflows.utils.set_workflow_for_object(workflow)

    def get_state(self):
        """Returns the current workflow state of the object.
        """
        return workflows.utils.get_state(self)

    def set_state(self, state):
        """Sets the workflow state of the object.
        """
        return workflows.utils.set_state(self, state)

    def set_initial_state(self):
        """Sets the initial state of the current workflow to the object.
        """
        return self.set_state(self.get_workflow().initial_state)

    def get_allowed_transitions(self, user):
        """Returns allowed transitions for the current state.
        """
        return workflows.utils.get_allowed_transitions(self, user)

    def do_transition(self, transition):
        """Processes the passed transition (if allowed).
        """
        return workflows.utils.do_transition(self, transition)

class Workflow(models.Model):
    """A workflow consists of a sequence of connected (through transitions)
    states. It can be assigned to a model and / or model instances. If a
    model instance has worklflow it takes precendence over the model's
    workflow.

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

    def get_objects(self):
        """Returns all objects which have this workflow assigned. Globally
        (via the object's content type) or locally (via the object itself).
        """
        objs = []

        # Get all objects whose content type has this workflow
        for wmr in WorkflowModelRelation.objects.filter(workflow=self):
            ctype = wmr.content_type
            # We have also to check whether the global workflow is not
            # overwritten.
            for obj in ctype.model_class().objects.all():
                if workflows.utils.get_workflow(obj) == self:
                    objs.append(obj)

        # Get all objects whose local workflow this workflow
        for wor in WorkflowObjectRelation.objects.filter(workflow=self):
            if wor.content not in objs:
                objs.append(wor.content)

        return objs

    def set_to(self, ctype_or_obj):
        """Sets the workflow to passed content type or object. See the specific
        methods for more information.

        **Parameters:**

        ctype_or_obj
            The content type or the object to which the workflow should be set.
            Can be either a ContentType instance or any Django model instance.
        """
        if isinstance(ctype_or_obj, ContentType):
            return self.set_to_model(ctype_or_obj)
        else:
            return self.set_to_object(ctype_or_obj)

    def set_to_model(self, ctype):
        """Sets the workflow to the passed content type. If the content
        type has already an assigned workflow the workflow is overwritten.

        **Parameters:**

        ctype
            The content type which gets the workflow. Can be any Django model
            instance.
        """
        try:
            wor = WorkflowModelRelation.objects.get(content_type=ctype)
        except WorkflowModelRelation.DoesNotExist:
            WorkflowModelRelation.objects.create(content_type=ctype, workflow=self)
        else:
            wor.workflow = self
            wor.save()

    def set_to_object(self, obj):
        """Sets the workflow to the passed object.

        If the object has already the given workflow nothing happens. Otherwise
        the workflow is set to the objectthe state is set to the workflow's
        initial state.

        **Parameters:**

        obj
            The object which gets the workflow.
        """
        ctype = ContentType.objects.get_for_model(obj)
        try:
            wor = WorkflowObjectRelation.objects.get(content_type=ctype, content_id=obj.id)
        except WorkflowObjectRelation.DoesNotExist:
            WorkflowObjectRelation.objects.create(content = obj, workflow=self)
            workflows.utils.set_state(obj, self.initial_state)
        else:
            if wor.workflow != self:
                wor.workflow = self
                wor.save()
                workflows.utils.set_state(self.initial_state)

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

class StateInheritanceBlock(models.Model):
    """Stores inheritance block for state and permission.

    **Attributes:**

    state
        The state for which the inheritance is blocked. Needs to be a State
        instance.
    permission
        The permission for which the instance is blocked. Needs to be a
        Permission instance.
    """
    state = models.ForeignKey(State, verbose_name=_(u"State"))
    permission = models.ForeignKey(Permission, verbose_name=_(u"Permission"))

    def __unicode__(self):
        return "%s %s" % (self.state.name, self.permission.name)

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