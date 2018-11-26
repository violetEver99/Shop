from __future__ import unicode_literals

from django.db import models

# Create your models here.
class userActionLog(models.Model):
    """"""
    username = models.CharField(max_length=100)
    ipaddr = models.CharField(max_length=200, blank=True, null=True)
    action = models.CharField(max_length=500)
    action_time = models.DateTimeField(auto_now_add=True)
    app = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.username       
