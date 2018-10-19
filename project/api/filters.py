from ast import literal_eval as make_tuple

from django.contrib.gis.geos import Polygon
from django_filters import FilterSet, Filter, DateFilter, BaseInFilter, widgets

from .models import Territory


class TerritoryFilter(FilterSet):
    bounds = Filter(method="filter_bounds")
    date = DateFilter(method="filter_date")
    exclude_ids = BaseInFilter(
        field_name="id", exclude=True, widget=widgets.CSVWidget()
    )

    def filter_bounds(self, queryset, field_name, value):
        geom = Polygon(make_tuple(value), srid=4326)
        return queryset.filter(geo__intersects=geom)

    def filter_date(self, queryset, field_name, value):
        return queryset.filter(start_date__lte=value, end_date__gte=value)

    class Meta:
        model = Territory
        fields = ("entity",)
