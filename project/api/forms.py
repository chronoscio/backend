from django import forms
from django.contrib.gis import geos, gdal
from .models import Territory
from zipfile import ZipFile
from tempfile import mkdtemp
from django.core.exceptions import ValidationError
import glob
import shutil


class TerritoryForm(forms.ModelForm):

    shape_file = forms.FileField(required=False)

    def save(self, commit=True):

        model = super(TerritoryForm, self).save(commit=False)
        if not self.cleaned_data['shape_file'] is None:
            shape_file = self.cleaned_data['shape_file']
            working_dir = mkdtemp()
            try:
                shape_zip = ZipFile(shape_file)
                shape_zip.extractall(working_dir)
            except:
                shutil.rmtree(working_dir)
                raise ValidationError("Could not extract zipfile.")

            shapes_list = glob.glob(working_dir + '/*.shp')

            try:
                ds = gdal.DataSource(shapes_list[0])
                layer = ds[0]
                polygons = []
                for feature in layer:
                    geom = feature.geom.geos
                    if type(geom) == geos.Polygon:
                        polygons.append(geom)

                if len(polygons) > 0:
                    multipoly = geos.MultiPolygon(polygons)
                    model.geo = multipoly.geojson
            except:
                shutil.rmtree(working_dir)
                raise ValidationError("Error converting shapefile")
                
        if commit:
            model.save()

        return model

    class Meta:
        model = Territory
        exclude = []
