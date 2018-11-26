from __future__ import unicode_literals

from django.db import models

class mainMenu(models.Model):
    name = models.CharField(max_length = 20)
    url = models.CharField(max_length = 500)
    class Meta:
        permissions=(('view_mainmenu', 'View mainmenu'),)    
    
class subMenu(models.Model):
    name = models.CharField(max_length = 20)
    url = models.CharField(max_length = 500)
    parentMenu = models.ForeignKey(mainMenu)
    class Meta:
        permissions=(('view_submenu', 'View submenu'),)    

class contentUrl(models.Model):
    name = models.CharField(max_length = 20)
    url = models.CharField(max_length = 500)
    parentMenu = models.ForeignKey(subMenu)
    class Meta:
        permissions=(('view_contenturl', 'View contenturl'),)