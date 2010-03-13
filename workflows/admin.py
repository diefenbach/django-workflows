from django.contrib import admin
from workflows.models import Workflow
from workflows.models import State
from workflows.models import Transition
from workflows.models import WorkflowObjectRelation
from workflows.models import WorkflowModelRelation
from workflows.models import WorkflowPermissionRelation
from workflows.models import StatePermissionRelation

class StateInline(admin.TabularInline):
    model = State

class WorkflowAdmin(admin.ModelAdmin):
    inlines = [
        StateInline,
    ]

admin.site.register(Workflow, WorkflowAdmin)

admin.site.register(State)
admin.site.register(Transition)
admin.site.register(WorkflowObjectRelation)
admin.site.register(WorkflowModelRelation)
admin.site.register(WorkflowPermissionRelation)
admin.site.register(StatePermissionRelation)
