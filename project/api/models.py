from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords

# Create your models here.
class Nation(models.Model):
    name = models.SlugField(max_length=20)
    local_name = models.CharField(max_length=30)
    wikipedia = models.URLField()
    history = HistoricalRecords()

    def __str__(self):
        return self.name

class Territory(models.Model):

    class Meta:
        verbose_name_plural = "territories"

    start_date = models.DateField()
    end_date = models.DateField()
    geo = models.GeometryField()
    nation = models.ForeignKey(Nation,
                               related_name='territories',
                               on_delete=models.CASCADE)
    history = HistoricalRecords()

    def clean(self, *args, **kwargs):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date")
        super(Territory, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Territory, self).save(*args, **kwargs)

    def __str__(self):
        return '%s: %s - %s' % (self.nation.name,
                                self.start_date.strftime('%m/%d/%Y'),
                                self.end_date.strftime('%m/%d/%Y'))
