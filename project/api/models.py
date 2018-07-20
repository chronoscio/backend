from django.core.exceptions import ValidationError
from django.contrib.gis.db import models

# Create your models here.
class Nation(models.Model):
    name = models.SlugField(max_length=20)
    local_name = models.CharField(max_length=30)
    wikipedia = models.URLField()

    def __str___(self):
        return self.name

class Territory(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    geo = models.GeometryField()

    nation = models.ForeignKey(Nation,
                               related_name='territories',
                               on_delete=models.CASCADE)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError('Start date must be before or equal to end date.')

    def __str__(self):
        return '%s: %s - %s' % (self.nation.name,
                                self.start_date.strftime('%m/%d/%Y'),
                                self.end_date.strftime('%m/%d/%Y'))
