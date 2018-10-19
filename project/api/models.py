from json import loads

from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from simple_history.models import HistoricalRecords
from colorfield.fields import ColorField
from polymorphic.models import PolymorphicModel, PolymorphicManager

# Create your models here.


class EntityManager(PolymorphicManager):
    """
    Manager for the Nation model to handle lookups by url_id
    """

    def get_by_natural_key(self, url_id):
        return self.get(url_id=url_id)


class Entity(PolymorphicModel):
    """
    Cultural/governmental entity. Serves as foreign key for most Territories
    """

    objects = EntityManager()

    name = models.TextField(
        max_length=100,
        help_text="Canonical name, should not include any epithets, must be unique",
        unique=True,
    )
    url_id = models.SlugField(
        max_length=75,
        help_text="Identifier used to lookup Entities in the URL, "
        "should be kept short and must be unique",
        unique=True,
    )
    history = HistoricalRecords()

    # required fields
    references = ArrayField(models.TextField(max_length=150))
    links = ArrayField(models.URLField(), default=list)
    description = models.TextField(
        help_text="Flavor text, brief history, etc.", blank=True
    )
    aliases = ArrayField(
        models.TextField(max_length=100),
        help_text="Alternative names this state may be known by",
        default=list,
    )

    def natural_key(self):
        return self.url_id

    def __str__(self):
        return self.name


class PoliticalEntity(Entity):
    """
    Cultural/governmental entity. Serves as foreign key for most Territories
    """

    color = ColorField(
        help_text="Color to display on map", unique=True, null=True, blank=True
    )
    history = HistoricalRecords()

    CONTROL_TYPE_CHOICES = (
        ("CC", "Complete Control"),
        ("DT", "Disputed Territory"),
        # TODO: Add more types later
    )
    control_type = models.TextField(
        max_length=2, choices=CONTROL_TYPE_CHOICES, default="CC", blank=True
    )

    # History fields

    # Foreign key to auth.User which will be updated every time the model is changed,
    # and is this stored in history as the user to update a specific revision
    # Consider other metadata (DateTime) for the revision (may be handled by django-simple-history)
    # TODO: implement this


class Territory(models.Model):
    """
    Defines the borders and controlled territories associated with an Entity.
    """

    class Meta:
        verbose_name_plural = "territories"

    start_date = models.DateField(help_text="When this border takes effect")
    end_date = models.DateField(help_text="When this border ceases to exist")
    geo = models.GeometryField()
    entity = models.ForeignKey(
        Entity, related_name="territories", on_delete=models.CASCADE
    )
    references = ArrayField(models.TextField(max_length=150))
    history = HistoricalRecords()

    def clean(self, *args, **kwargs):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date")
        if (
            loads(self.geo.json)["type"] != "Polygon"
            and loads(self.geo.json)["type"] != "MultiPolygon"
        ):
            raise ValidationError(
                "Only Polygon and MultiPolygon objects are acceptable geometry types."
            )

        try:
            # This date check is inculsive.
            if Territory.objects.filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
                entity__exact=self.entity,
            ).exists():
                raise ValidationError(
                    "Another territory of this PoliticalEntity exists during this timeframe."
                )
        except Entity.DoesNotExist:
            pass

        super(Territory, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Territory, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: %s - %s" % (
            self.entity.name,
            self.start_date.strftime("%m/%d/%Y"),
            self.end_date.strftime("%m/%d/%Y"),
        )


class DiplomaticRelation(models.Model):
    """
    Defines political and diplomatic interactions between PoliticalEntitys.
    """

    start_date = models.DateField(help_text="When this relation takes effect")
    end_date = models.DateField(help_text="When this relation ceases to exist")
    parent_parties = models.ManyToManyField(
        PoliticalEntity, related_name="parent_parties"
    )
    child_parties = models.ManyToManyField(
        PoliticalEntity, related_name="child_parties"
    )
    DIPLO_TYPE_CHOICES = (
        ("A", "Military Alliance"),
        ("D", "Dual Monarchy"),
        ("M", "Condominium"),
        ("T", "Trade League"),
        ("W", "At War"),
        ("P", "State or Province"),
        ("CP", "Client State - Puppet State"),
        ("CV", "Client State - Vassal State"),
        ("CPU", "Client State - Personal Union"),
        ("CCR", "Client State - Colony - Royal"),
        ("CCP", "Client State - Colony - Propreitary"),
        ("CCC", "Client State - Colony - Charter"),
    )
    diplo_type = models.TextField(max_length=3, choices=DIPLO_TYPE_CHOICES)
    references = ArrayField(models.TextField(max_length=150))

    history = HistoricalRecords()

    def clean(self, *args, **kwargs):
        if self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date")

        super(DiplomaticRelation, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(DiplomaticRelation, self).save(*args, **kwargs)

    def __str__(self):
        return "%s - %s: %s - %s" % (
            self.parent_parties.all()[0].name,
            self.child_parties.all()[0].name,
            self.start_date.strftime("%m/%d/%Y"),
            self.end_date.strftime("%m/%d/%Y"),
        )
