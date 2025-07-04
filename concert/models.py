from django.db import models
from django.utils import timezone
from datetime import datetime, timezone
from catalog.models import Composer, Work 

# Create your models here.
class Area(models.Model):
    name = models.CharField(max_length=250)

class Facility(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('area', 'name',)

class Concert(models.Model):
    kopis_id = models.CharField(max_length=8, primary_key=True)
    prfnm = models.CharField(max_length=250)
    datetime = models.DateTimeField()
    prfruntime = models.CharField(max_length=10)
    price = models.CharField(max_length=250)
    facility = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, related_name='areas', on_delete=models.SET_NULL, null=True)
    prfcast = models.CharField(max_length=250, default="")
    display_poster_name = models.CharField(max_length=250, default="")
    program_blurb = models.CharField(max_length=1000, default="")

    @property
    def is_past(self):
        return datetime.now(timezone.utc) > self.datetime

    def __str__(self):
        return self.kopis_id

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['kopis_id', 'datetime'], name='kopis_id_datetime_unique_combination'
            )
        ]

class Program(models.Model):
    concert = models.ForeignKey(Concert, related_name='compositions', on_delete=models.CASCADE)
    composer = models.CharField(max_length=250)
    work = models.CharField(max_length=250)
    composer_fuzzy_match = models.ForeignKey(Composer, default="", null=True, on_delete=models.PROTECT)
    work_fuzzy_match = models.ForeignKey(Work, default="", null=True, on_delete=models.PROTECT)
    composer_fuzzy_match_confidence = models.FloatField(default=0.0)
    work_fuzzy_match_confidence = models.FloatField(default=0.0)

class Performer(models.Model):
    concert = models.ForeignKey(Concert, related_name='performers', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)

    class Meta:
        unique_together = ('concert', 'name',)

class TicketVendor(models.Model):
    concert = models.ForeignKey(Concert, related_name='ticket_vendors', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    url = models.URLField(max_length=250)
    class Meta:
        unique_together = ('concert', 'name', 'url',)

class FullPosterName(models.Model):
    concert = models.ForeignKey(Concert, related_name='full_poster_names', on_delete=models.CASCADE)
    name = models.CharField(max_length=250)

    class Meta:
        unique_together = ('concert', 'name',)
