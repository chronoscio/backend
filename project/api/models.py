from json import loads

from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from simple_history.models import HistoricalRecords
from colorfield.fields import ColorField

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
    color = ColorField(help_text="Color to display on map",
                       unique=True,
                       null=True,
                       blank=True)
    history = HistoricalRecords()

    # Flavor fields

    # required fields
    references = ArrayField(
        models.TextField(max_length=150),
    )

    # optional fields
    aliases = ArrayField(
        models.TextField(max_length=100),
        help_text="Alternative names this state may be known by",
        blank=True,
    )
    description = models.TextField(help_text="Flavor text, brief history, etc.",
                                   blank=True)
    links = ArrayField(
        models.URLField(),
        blank=True,
    )
    CONTROL_TYPE_CHOICES = (
        ("CC", "Complete Control"),
        ("DT", "Disputed Territory"),
        # TODO: Add more types later
    )
    control_type = models.TextField(
        max_length=2,
        choices=CONTROL_TYPE_CHOICES,
        default="CC",
        blank=True,
    )

    # History fields

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
    references = ArrayField(
        models.TextField(max_length=150),
    )
    history = HistoricalRecords()

    def clean(self, *args, **kwargs):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date")
        if loads(self.geo.json)["type"] != "Polygon" and loads(self.geo.json)["type"] != "MultiPolygon":
            raise ValidationError(
                "Only Polygon and MultiPolygon objects are acceptable geometry types.")

        # This date check is inculsive.
        if Territory.objects.filter(start_date__lte=self.end_date, end_date__gte=self.start_date, nation__exact=self.nation).exists():
            raise ValidationError(
                "Another territory of this nation exists during this timeframe.")

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
    Defines political and diplomatic interactions between Nations.
    """
    start_date = models.DateField(help_text="When this relation takes effect")
    end_date = models.DateField(help_text="When this relation ceases to exist")
    parent_parties = models.ManyToManyField(
        Nation, related_name='parent_parties')
    child_parties = models.ManyToManyField(
        Nation, related_name='child_parties')
    DIPLO_TYPE_CHOICES = (
        ("A", "Military Alliance"),
        ("D", "Dual Monarchy"),
        ("M", "Condominium"),
        ("T", "Trade League"),
        ("W", "At War"),
        ('P', 'State or Province'),
        ("CP", "Client State - Puppet State"),
        ("CV", "Client State - Vassal State"),
        ("CPU", "Client State - Personal Union"),
        ("CCR", "Client State - Colony - Royal"),
        ("CCP", "Client State - Colony - Propreitary"),
        ("CCC", "Client State - Colony - Charter"),
    )
    diplo_type = models.TextField(
        max_length=3,
        choices=DIPLO_TYPE_CHOICES,
    )
    references = ArrayField(
        models.TextField(max_length=150),
    )

    history = HistoricalRecords()

    def clean(self, *args, **kwargs):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date")

        super(DiplomaticRelation, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(DiplomaticRelation, self).save(*args, **kwargs)

    def __str__(self):
        return "%s - %s: %s - %s" % (self.parent_parties.all()[0].name,
                                     self.child_parties.all()[0].name,
                                     self.start_date.strftime("%m/%d/%Y"),
                                     self.end_date.strftime("%m/%d/%Y"))
