# django imports
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sessions.backends.file import SessionStore
from django.core.handlers.wsgi import WSGIRequest
from django.test.client import Client

# workflows import
import permissions.utils
import workflows.utils
from workflows.models import State
from workflows.models import StateInheritanceBlock
from workflows.models import StatePermissionRelation
from workflows.models import StateObjectRelation
from workflows.models import Transition
from workflows.models import Workflow
from workflows.models import WorkflowModelRelation
from workflows.models import WorkflowObjectRelation
from workflows.models import WorkflowPermissionRelation

class WorkflowTestCase(TestCase):
    """Tests a simple workflow without permissions.
    """
    def setUp(self):
        """
        """
        create_workflow(self)

    def test_get_states(self):
        """
        """
        states = self.w.states.all()
        self.assertEqual(states[0], self.private)
        self.assertEqual(states[1], self.public)

    def test_transitions(self):
        """
        """
        transitions = self.public.transitions.all()
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0], self.make_private)

        transitions = self.private.transitions.all()
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0], self.make_public)

    def test_get_transitions(self):
        """
        """
        request = create_request()
        transitions = self.private.get_allowed_transitions(request.user)
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0], self.make_public)

        transitions = self.public.get_allowed_transitions(request.user)
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0], self.make_private)

    def test_unicode(self):
        """
        """
        self.assertEqual(self.w.__unicode__(), u"Standard")

class PermissionsTestCase(TestCase):
    """Tests a simple workflow with permissions.
    """
    def setUp(self):
        """
        """
        create_workflow(self)

        # Register groups
        self.anonymous = permissions.utils.register_group("Anonymous")
        self.owner = permissions.utils.register_group("Owner")

        self.user = User.objects.create(username="john")
        self.user.groups.add(self.owner)
        self.user.save()

        # Example content type
        self.page_1 = FlatPage.objects.create(url="/page-1/", title="Page 1")

        # Registers permissions
        self.view = permissions.utils.register_permission("View", "view")
        self.edit = permissions.utils.register_permission("Edit", "edit")

        # Add all permissions which are managed by the workflow
        wpr = WorkflowPermissionRelation.objects.create(workflow=self.w, permission=self.view)
        wpr = WorkflowPermissionRelation.objects.create(workflow=self.w, permission=self.edit)

        # Add permissions for single states
        spr = StatePermissionRelation.objects.create(state=self.public, permission=self.view, group=self.owner)
        spr = StatePermissionRelation.objects.create(state=self.private, permission=self.view, group=self.owner)
        spr = StatePermissionRelation.objects.create(state=self.private, permission=self.edit, group=self.owner)

        # Add inheritance block for single states
        sib = StateInheritanceBlock.objects.create(state=self.private, permission=self.view)
        sib = StateInheritanceBlock.objects.create(state=self.private, permission=self.edit)
        sib = StateInheritanceBlock.objects.create(state=self.public, permission=self.edit)

        workflows.utils.set_workflow(self.page_1, self.w)

    def test_set_state(self):
        """
        """
        # Permissions
        result = permissions.utils.has_permission(self.page_1, "edit", self.user)
        self.assertEqual(result, True)

        result = permissions.utils.has_permission(self.page_1, "view", self.user)
        self.assertEqual(result, True)

        # Inheritance
        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, False)

        result = permissions.utils.is_inherited(self.page_1, "edit")
        self.assertEqual(result, False)

        # Change state
        workflows.utils.set_state(self.page_1, self.public)

        # Permissions
        result = permissions.utils.has_permission(self.page_1, "edit", self.user)
        self.assertEqual(result, False)

        result = permissions.utils.has_permission(self.page_1, "view", self.user)
        self.assertEqual(result, True)

        # Inheritance
        result = permissions.utils.is_inherited(self.page_1, "view")
        self.assertEqual(result, True)

        result = permissions.utils.is_inherited(self.page_1, "edit")
        self.assertEqual(result, False)

    def test_do_transition(self):
        """
        """
        state = workflows.utils.get_state(self.page_1)
        self.assertEqual(state.name, self.private.name)

        workflows.utils.do_transition(self.page_1, self.make_public, self.user)

        state = workflows.utils.get_state(self.page_1)
        self.assertEqual(state.name, self.public.name)

class UtilsTestCase(TestCase):
    """Tests various methods of the utils module.
    """
    def setUp(self):
        """
        """
        create_workflow(self)
        self.user = User.objects.create()

    def test_workflow(self):
        """
        """
        workflows.utils.set_workflow(self.user, self.w)
        result = workflows.utils.get_workflow(self.user)
        self.assertEqual(result, self.w)

    def test_state(self):
        """
        """
        workflows.utils.set_workflow(self.user, self.w)
        result = workflows.utils.get_state(self.user)
        self.assertEqual(result, self.w.initial_state)

    def test_get_objects_for_workflow_1(self):
        """Workflow is added to object.
        """
        result = workflows.utils.get_objects_for_workflow(self.w)
        self.assertEqual(result, [])

        workflows.utils.set_workflow(self.user, self.w)
        result = workflows.utils.get_objects_for_workflow(self.w)
        self.assertEqual(result, [self.user])

    def test_get_objects_for_workflow_2(self):
        """Workflow is added to content type.
        """
        result = workflows.utils.get_objects_for_workflow(self.w)
        self.assertEqual(result, [])
        
        ctype = ContentType.objects.get_for_model(self.user)
        workflows.utils.set_workflow(ctype, self.w)
        result = workflows.utils.get_objects_for_workflow(self.w)
        self.assertEqual(result, [self.user])

    def test_get_objects_for_workflow_3(self):
        """Workflow is added to content type and object.
        """
        result = workflows.utils.get_objects_for_workflow(self.w)
        self.assertEqual(result, [])

        workflows.utils.set_workflow(self.user, self.w)
        result = workflows.utils.get_objects_for_workflow(self.w)
        self.assertEqual(result, [self.user])
        
        ctype = ContentType.objects.get_for_model(self.user)
        workflows.utils.set_workflow(ctype, self.w)
        result = workflows.utils.get_objects_for_workflow(self.w)
        self.assertEqual(result, [self.user])

class StateTestCase(TestCase):
    """Tests the State model
    """
    def setUp(self):
        """
        """
        create_workflow(self)

    def test_unicode(self):
        """
        """
        self.assertEqual(self.private.__unicode__(), u"Private")

class TransitionTestCase(TestCase):
    """Tests the Transition model
    """
    def setUp(self):
        """
        """
        create_workflow(self)

    def test_unicode(self):
        """
        """
        self.assertEqual(self.make_private.__unicode__(), u"Make private")

class RelationsTestCase(TestCase):
    """Tests various Relations models.
    """
    def setUp(self):
        """
        """
        create_workflow(self)
        self.page_1 = FlatPage.objects.create(url="/page-1/", title="Page 1")

    def test_unicode(self):
        """
        """
        # WorkflowObjectRelation
        workflows.utils.set_workflow(self.page_1, self.w)
        wor = WorkflowObjectRelation.objects.filter()[0]
        self.assertEqual(wor.__unicode__(), "flat page 1 - Standard")

        # StateObjectRelation
        workflows.utils.set_state(self.page_1, self.public)
        sor = StateObjectRelation.objects.filter()[0]
        self.assertEqual(sor.__unicode__(), "flat page 1 - Public")

        # WorkflowModelRelation
        ctype = ContentType.objects.get_for_model(self.page_1)
        workflows.utils.set_workflow(ctype, self.w)
        wmr = WorkflowModelRelation.objects.filter()[0]
        self.assertEqual(wmr.__unicode__(), "flat page - Standard")

        # WorkflowPermissionRelation
        self.view = permissions.utils.register_permission("View", "view")
        wpr = WorkflowPermissionRelation.objects.create(workflow=self.w, permission=self.view)
        self.assertEqual(wpr.__unicode__(), "Standard View")

        # StatePermissionRelation
        self.owner = permissions.utils.register_group("Owner")
        spr = StatePermissionRelation.objects.create(state=self.public, permission=self.view, group=self.owner)
        self.assertEqual(spr.__unicode__(), "Public Owner View")

# Helpers ####################################################################

def create_workflow(self):
    self.w = Workflow.objects.create(name="Standard")

    self.private = State.objects.create(name="Private", workflow= self.w)
    self.public = State.objects.create(name="Public", workflow= self.w)

    self.make_public = Transition.objects.create(name="Make public", workflow=self.w, destination = self.public)
    self.make_private = Transition.objects.create(name="Make private", workflow=self.w, destination = self.private)

    self.private.transitions.add(self.make_public)
    self.public.transitions.add(self.make_private)

    self.w.initial_state = self.private
    self.w.save()

# Taken from "http://www.djangosnippets.org/snippets/963/"
class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.

    Usage:

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

    This class re-uses the django.test.client.Client interface, docs here:
    http://www.djangoproject.com/documentation/testing/#the-test-client

    Once you have a request object you can pass it to any view function,
    just as if that view had been hooked up using a URLconf.

    """
    def request(self, **request):
        """
        Similar to parent class, but returns the request object as soon as it
        has created it.
        """
        environ = {
            'HTTP_COOKIE': self.cookies,
            'PATH_INFO': '/',
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': 80,
            'SERVER_PROTOCOL': 'HTTP/1.1',
        }
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)

def create_request():
    """
    """
    rf = RequestFactory()
    request = rf.get('/')
    request.session = SessionStore()

    user = User()
    user.is_superuser = True
    user.save()
    request.user = user

    return request
