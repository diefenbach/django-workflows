# django imports
from django import template

# workflows imports
import workflows.utils
 
register = template.Library()

@register.inclusion_tag('workflows/transitions.html', takes_context=True)
def transitions(context, obj):
    """
    """
    workflows.utils.get_transitions(obj)
    
    return {
        "categories" : categories,
    }
