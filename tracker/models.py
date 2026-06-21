# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DimNeighborhoods(models.Model):
    neighborhoodid = models.AutoField(db_column='NeighborhoodID', primary_key=True)  # Field name made lowercase.
    neighbourhoodgroup = models.CharField(db_column='NeighbourhoodGroup', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    neighbourhood = models.CharField(db_column='Neighbourhood', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Dim_Neighborhoods'
        unique_together = (('neighbourhoodgroup', 'neighbourhood'),)


class FactListings(models.Model):
    listingid = models.BigIntegerField(db_column='ListingID', primary_key=True)  # Field name made lowercase.
    listingname = models.CharField(db_column='ListingName', max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    hostid = models.BigIntegerField(db_column='HostID')  # Field name made lowercase.
    roomtype = models.CharField(db_column='RoomType', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    constructionyear = models.IntegerField(db_column='ConstructionYear', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Fact_Listings'


class LogDailyprices(models.Model):
    logid = models.AutoField(db_column='LogID', primary_key=True)  # Field name made lowercase.
    listingid = models.ForeignKey(FactListings, models.DO_NOTHING, db_column='ListingID')  # Field name made lowercase.
    recorddate = models.DateField(db_column='RecordDate', blank=True, null=True)  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    servicefee = models.DecimalField(db_column='ServiceFee', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Log_DailyPrices'
