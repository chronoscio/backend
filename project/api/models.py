from django.contrib.gis.db import models
from required import Requires, R

# Create your models here.
class Nation(models.Model):
    name = models.SlugField(max_length=20)
    local_name = models.CharField(max_length=30)
    wikipedia = models.URLField()

class Territory(models.Model):
    REQUIREMENTS = (
        Requires("end_date", "start_date") +
        Requires("end_date", R("end_date") > R("start_date"))
    )

    start_date = models.DateField()
    end_date = models.DateField()

    geo = models.GeometryField()

    nation = models.ForeignKey(Nation, on_delete=models.CASCADE)

    def validate(self, data):
        self.REQUIREMENTS.validate(data)
