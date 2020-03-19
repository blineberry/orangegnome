from django import template
from ..models import Profile

register = template.Library()

@register.inclusion_tag('pages/_owner_card.html')
def owner_card():
    owner = Profile.objects.get_owner()   

    return { 'owner': owner }
    
def site_meta():
    owner = Profile.objects.get_owner()
    return { 'owner': owner }