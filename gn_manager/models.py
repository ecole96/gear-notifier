from django.db import models
from django.conf import settings

class Entry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    query = models.CharField(max_length=250,help_text="This is what will be searched. Be as specific as possible. Max: 250 characters.")
    min_price = models.DecimalField(max_digits=11,decimal_places=2,null=True,blank=True,verbose_name="Minimum Price ($)")
    max_price = models.DecimalField(max_digits=11,decimal_places=2,null=True,blank=True,verbose_name="Maximum Price ($)")
    cl = models.BooleanField(default=True,verbose_name='Craigslist')
    gc = models.BooleanField(default=True,verbose_name='Guitar Center')
    rv = models.BooleanField(default=True,verbose_name='Reverb')
    initiallyScanned = models.BooleanField(default=False,verbose_name='Initially scanned?')

    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

    def __str__(self):
        return ', '.join([self.user.email,self.query])


