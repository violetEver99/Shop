from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    theme = models.CharField(max_length=10,default='classic')
    info = models.CharField(max_length=200, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    sa = models.BooleanField(default=False)
    level = models.CharField(max_length=20, blank=True, null=True)
    
    
    def __unicode__(self):
        return self.user.username    
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        #UserProfile.objects.create(user=instance)
        profile = UserProfile()
        profile.user = instance
        profile.save()        

#def set_user_profile(key,value):
post_save.connect(create_user_profile, sender=User)


class Perms(models.Model):
    """"""
    data = models.CharField(max_length=200, null=False)
    datatype = models.CharField(max_length=50, null=False)

class Group_Perms(models.Model):
    group = models.ForeignKey(Group)
    perms = models.ForeignKey(Perms)

class GroupProfile(models.Model):
    # This field is required.
    group = models.OneToOneField(Group)

    # Other fields here
    usable = models.BooleanField(default=0)
    info = models.CharField(max_length=200, blank=True, null=True)
    
    def __unicode__(self):
        return self.group.name    
    
    
def create_group_profile(sender, instance, created, **kwargs):
    if created:
        #UserProfile.objects.create(user=instance)
        profile = GroupProfile()
        profile.group = instance
        profile.save()     

#def set_user_profile(key,value):
post_save.connect(create_group_profile, sender=Group)


