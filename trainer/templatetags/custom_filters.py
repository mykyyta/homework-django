from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.filter(name=group_name).first()
    return group is not None and group in user.groups.all()