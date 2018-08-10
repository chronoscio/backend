from json import loads
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from simple_history.models import HistoricalRecords
from colorfield.fields import ColorField
from rest_framework.authtoken.models import Token

# Create your models here.
class Nation(models.Model):
    """
    Cultural/governmental entity. Serves as foreign key for most Territories
    """
    name = models.TextField(max_length=100,
                            help_text="Canonical name, should not include any epithets, must be unique",
                            unique=True)
    url_id = models.SlugField(max_length=75,
                              help_text="Identifier used to lookup nations in the URL, "
                                        "should be kept short and must be unique",
                              unique=True)
    color = ColorField(default="#FF0000",
                       help_text="Color to display on map",
                       unique=True)
    history = HistoricalRecords()

    #Flavor fields
    aliases = ArrayField(
        models.TextField(max_length=100),
        help_text="Alternative names this state may be known by",
        null=True,
        blank=True
    )
    description = models.TextField(help_text="Flavor text, brief history, etc.",
                                   blank=True)
    wikipedia = models.URLField(help_text="Link to the Wikipedia article for this nation",
                                blank=True)

    #History fields

    # Foreign key to auth.User which will be updated every time the model is changed,
    # and is this stored in history as the user to update a specific revision
    # Consider other metadata (DateTime) for the revision (may be handled by django-simple-history)
    # TODO: implement this

    def __str__(self):
        return self.name

class Territory(models.Model):
    """
    Defines the borders and controlled territories associated with a Nation.
    """
    class Meta:
        verbose_name_plural = "territories"

    start_date = models.DateField(help_text="When this border takes effect")
    end_date = models.DateField(help_text="When this border ceases to exist")
    geo = models.GeometryField()

    nation = models.ForeignKey(Nation,
                               related_name="territories",
                               on_delete=models.CASCADE)
    CONTROL_TYPE_CHOICES = (
        ("CC", "Complete Control"),
        ("DT", "Disputed Territory"),
        # TODO: Add more types later, drawing a blank atm
    )
    control_type = models.TextField(
        max_length=2,
        choices=CONTROL_TYPE_CHOICES,
        default="CC",
    )
    history = HistoricalRecords()

    def clean(self, *args, **kwargs):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date")
        if loads(self.geo.json)["type"] != "Polygon" and loads(self.geo.json)["type"] != "MultiPolygon":
            raise ValidationError("Only Polygon and MultiPolygon objects are acceptable geometry types")
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

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Automatically creates a token when a user is registered
    """
    if created:
        Token.objects.create(user=instance)
