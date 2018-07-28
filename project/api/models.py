from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from colorfield.fields import ColorField

# Create your models here.
class Nation(models.Model):
    """
    Cultural/governmental entity. Serves as foreign key for most Territories
    """
    name = models.SlugField(max_length=20,
                            help_text="Canonical name, should not include any epithets, must be unique",
                            unique=True)
    color = ColorField(default="#FF0000",
                       help_text="Color to display on map")
    history = HistoricalRecords()

    #Flavor fields
    aliases = models.TextField(help_text="CSV of alternative names this state may be known by",
                               blank=True)
    description = models.TextField(help_text="Flavor text, brief history, etc.",
                                   blank=True)
    wikipedia = models.URLField(blank=True,
                                help_text="Link to the Wikipedia article for this nation")

    def __str__(self):
        return self.name

class Territory(models.Model):
    """
    Defines the borders and controlled territories associated with a Nation.
    """
    start_date = models.DateField(help_text="When this border takes effect")
    end_date = models.DateField(help_text="When this border ceases to exist")
    geo = models.MultiPolygonField()
    nation = models.ForeignKey(Nation,
                               related_name="territories",
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
        return "%s: %s - %s" % (self.nation.name,
                                self.start_date.strftime("%m/%d/%Y"),
                                self.end_date.strftime("%m/%d/%Y"))

class DiplomaticRelation(models.Model):
    """
    Abstract class for relationships between states, including wars, alliances, overlordships, etc.
    This would be a whole 'nother project that should probably be primarily populated by Wikipedia scraping
    Some relations will most likely be controversial, for example the earldoms of Ireland swore allegiance to
        the English monarchs but in otherwise acted entirely independently, maybe have an autonomy slider
        or something similar?
    """
    pass
