from __future__ import unicode_literals

from django.db import models

# Create your models here.

#example
#class Missions(models.Model):
    #direction = models.CharField(max_length=50, null=True)
    #mid = models.CharField(max_length=20, null=False)
    #sender = models.CharField(max_length=20, null=False)
    #sendername = models.CharField(max_length=50, null=False)
    #senderphone = models.CharField(max_length=20, null=False)
    
    #majorcity = models.CharField(max_length=20, null=False)
    #assistcity = models.CharField(max_length=20, null=True)
    
    #receiptor = models.CharField(max_length=20, null=True)
    #receiptorname = models.CharField(max_length=50, null=True)
    #receiptorphone = models.CharField(max_length=20, null=True)
    #status = models.IntegerField(null=False)
    #dataid = models.CharField(max_length=20, null=True)
    
    #ischecked = models.IntegerField(null=True)
    #result = models.TextField(null=True)
    #codes = models.CharField(max_length=50, null=True)
    #project = models.CharField(max_length=50, null=True)
    #count = models.CharField(max_length=5, null=True)
    #attach = models.CharField(max_length=300,null=True)
    #date = models.DateTimeField()
    #def __unicode__(self):
        #return self.mid
    
class Auctions(models.Model):
    auctionid = models.CharField(max_length=20, null=False)
    auctionname = models.CharField(max_length=50, null=False)
    auctionprice = models.DecimalField(max_digits=9,  decimal_places=2)
    auctionnum = models.CharField(max_length=20, null=True)
    auctiondesc = models.CharField(max_length=200, null=True)
    #auctionpic = models.CharField(max_length=200, null=True)
    #auctionpicpath = models.CharField(max_length=200, null=True)
    def __unicode__(self):
        return self.auctionid
