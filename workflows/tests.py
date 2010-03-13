# django imports
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
from workflows.models import StatePermissionRelation
from workflows.models import Transition
from workflows.models import Workflow
from workflows.models import WorkflowPermissionRelation

class PermissionsTestCase(TestCase):
    """
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

        # Add permissions for the single states
        spr = StatePermissionRelation.objects.create(state=self.public, permission=self.view, group=self.owner)
        spr = StatePermissionRelation.objects.create(state=self.private, permission=self.view, group=self.owner)
        spr = StatePermissionRelation.objects.create(state=self.private, permission=self.edit, group=self.owner)

        workflows.utils.set_workflow(self.w, self.page_1)

    def test_set_state(self):
        """
        """
        result = permissions.utils.has_permission("edit", self.user, self.page_1)
        self.assertEqual(result, True)

        result = permissions.utils.has_permission("view", self.user, self.page_1)
        self.assertEqual(result, True)

        workflows.utils.set_state(self.page_1, self.public)

        result = permissions.utils.has_permission("edit", self.user, self.page_1)
        self.assertEqual(result, False)

        result = permissions.utils.has_permission("view", self.user, self.page_1)
        self.assertEqual(result, True)

class UtilsTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        create_workflow(self)
        self.user = User.objects.create()

    def test_workflow(self):
        """
        """
        workflows.utils.set_workflow(self.w, self.user)
        result = workflows.utils.get_workflow(self.user)
        self.assertEqual(result, self.w)

    def test_state(self):
        """
        """
        workflows.utils.set_workflow(self.w, self.user)
        result = workflows.utils.get_state(self.user)
        self.assertEqual(result, self.w.initial_state)

class WorkflowTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        create_workflow(self)

    def test_get_states(self):
        """
        """
        states = self.w.states.all()
        self.assertEqual(states[0], self.s1)
        self.assertEqual(states[1], self.s2)

    def test_transitions(self):
        """
        """
        transitions = self.s1.transitions.all()
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0], self.t2)

        transitions = self.s2.transitions.all()
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0], self.t1)

    def test_get_transitions(self):
        """
        """
        request = create_request()
        transitions = self.s1.get_allowed_transitions(request.user)
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0], self.t2)

        transitions = self.s2.get_allowed_transitions(request.user)
        self.assertEqual(len(transitions), 1)
        self.assertEqual(transitions[0], self.t1)

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
