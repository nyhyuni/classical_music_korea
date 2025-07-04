# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Composer(models.Model):
    name = models.TextField(unique=True, blank=True, null=True)
    name_ko = models.TextField(blank=True, null=True)
    lastname_ko = models.TextField(blank=True, null=True)
    complete_name = models.TextField(blank=True, null=True)
    portrait = models.TextField(blank=True, null=True)
    birth = models.DateField()
    death = models.DateField(blank=True, null=True)
    epoch = models.TextField()
    country = models.TextField(blank=True, null=True)
    recommended = models.BooleanField(blank=True, null=True)
    popular = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name


class Work(models.Model):
    composer = models.ForeignKey(Composer, models.DO_NOTHING)
    title = models.TextField(blank=True, null=True)
    title_ko = models.TextField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)
    subtitle_ko = models.TextField(blank=True, null=True)
    searchterms = models.TextField(blank=True, null=True)
    genre = models.TextField()
    year = models.DateField(blank=True, null=True)
    recommended = models.BooleanField(blank=True, null=True)
    popular = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name
