from django.db import models
from gn_manager.models import Entry
import datetime

class Match(models.Model):
    entry = models.ForeignKey(Entry,on_delete=models.CASCADE)
    url = models.URLField(max_length=500)

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __str__(self):
        return ', '.join([self.entry.user.email,self.entry.query,self.url])

class Misc(models.Model):
    lastrun_dt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Misc"
        verbose_name_plural = "Misc"

    def __str__(self):
        return datetime.datetime.strftime(self.lastrun_dt, "%m-%d-%Y %H:%M:%S")

