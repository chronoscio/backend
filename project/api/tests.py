import json
import requests

from django.conf import settings
from django.urls import reverse
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase
from os import environ

from .models import PoliticalEntity, Territory, DiplomaticRelation

# https://stackoverflow.com/a/815160/


def memoize(function):
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


@memoize
def getUserToken(client_id=settings.AUTH0_CLIENT_ID, client_secret=settings.AUTH0_CLIENT_SECRET):
    url = 'https://' + settings.AUTH0_DOMAIN + '/oauth/token'
    headers = {'content-type': 'application/json'}
    parameter = {"client_id": client_id,
                 'client_secret': client_secret,
                 "audience": settings.API_IDENTIFIER,
                 "grant_type": "client_credentials"}
    response = json.loads(requests.post(
        url, json=parameter, headers=headers).text)
    return response['access_token']


class ModelTest(TestCase):

    @classmethod
    def setUpTestData(self):
        """
        Create basic model instances and test user
        """
        new_PoliticalEntity = PoliticalEntity.objects.create(name="Test PoliticalEntity",
                                           url_id="test_PoliticalEntity",
                                           color="fff",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        new_PoliticalEntity.save()
        child_PoliticalEntity = PoliticalEntity.objects.create(name="Test Child PoliticalEntity",
                                           url_id="test_child_PoliticalEntity",
                                           color="ccc",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        child_PoliticalEntity.save()
        Territory.objects.create(start_date="0002-01-01",
                                 end_date="0004-01-01",
                                 entity=new_PoliticalEntity,
                                 references=[
                                     "https://en.wikipedia.org/wiki/Test"],
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        diprel = DiplomaticRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            references=["https://en.wikipedia.org/wiki/Test"],
            diplo_type='A',
        )
        diprel.parent_parties.add(new_PoliticalEntity)
        diprel.child_parties.add(child_PoliticalEntity)

    def test_model_can_create_politicalentity(self):
        """
        Ensure that we can create politicalentitys.
        """
        new_politicalentity = PoliticalEntity.objects.create(name="Test PoliticalEntity2",
                                           url_id="test_politicalentity2",
                                           color="ddd",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        new_politicalentity.save()
        self.assertTrue(PoliticalEntity.objects.filter(url_id="test_politicalentity2").exists())

    def test_model_can_create_territory(self):
        """
        Ensure that we can create territories. Specifically checks if we can create [start_date+1,end_date-1]
        """
        politicalentity = PoliticalEntity.objects.get(url_id="test_PoliticalEntity")
        Territory.objects.create(start_date="0007-01-01",
                                 end_date="0008-01-01",
                                 politicalentity=politicalentity,
                                 references=[
                                     "https://en.wikipedia.org/wiki/Test"],
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        self.assertTrue(Territory.objects.filter(
            politicalentity=politicalentity, start_date="0007-01-01", end_date="0008-01-01").exists())
        politicalentity = PoliticalEntity.objects.get(url_id="test_PoliticalEntity")
        Territory.objects.create(start_date="0004-01-02",
                                 end_date="0006-12-31",
                                 politicalentity=politicalentity,
                                 references=[
                                     "https://en.wikipedia.org/wiki/Test"],
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        self.assertTrue(Territory.objects.filter(
            politicalentity=politicalentity, start_date="0004-01-02", end_date="0006-12-31").exists())

    def test_model_can_not_create_territory(self):
        """
        Ensure that date checks work.
        """
        new_politicalentity = PoliticalEntity.objects.get(url_id="test_PoliticalEntity")
        with self.assertRaises(ValidationError):
            Territory.objects.create(start_date="0001-01-01",
                                     end_date="0003-01-01",
                                     politicalentity=new_politicalentity,
                                     references=[
                                         "https://en.wikipedia.org/wiki/Test"],
                                     geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        with self.assertRaises(ValidationError):
            Territory.objects.create(start_date="0002-01-01",
                                     end_date="0003-01-01",
                                     politicalentity=new_politicalentity,
                                     references=[
                                         "https://en.wikipedia.org/wiki/Test"],
                                     geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        with self.assertRaises(ValidationError):
            Territory.objects.create(start_date="0003-01-01",
                                     end_date="0005-01-01",
                                     politicalentity=new_politicalentity,
                                     references=[
                                         "https://en.wikipedia.org/wiki/Test"],
                                     geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        with self.assertRaises(ValidationError):
            Territory.objects.create(start_date="0001-01-01",
                                     end_date="0005-01-01",
                                     politicalentity=new_politicalentity,
                                     references=[
                                         "https://en.wikipedia.org/wiki/Test"],
                                     geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))


class APITest(APITestCase):

    @classmethod
    def setUpTestData(self):
        """
        Create basic model instances
        """
        new_PoliticalEntity = PoliticalEntity.objects.create(name="Test PoliticalEntity",
                                           url_id="test_PoliticalEntity",
                                           color="fff",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        new_PoliticalEntity.save()
        child_PoliticalEntity = PoliticalEntity.objects.create(name="Test Child PoliticalEntity",
                                           url_id="test_child_PoliticalEntity",
                                           color="ccc",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        child_PoliticalEntity.save()
        Territory.objects.create(start_date="0001-01-01",
                                 end_date="0005-01-01",
                                 entity=new_PoliticalEntity,
                                 references=[
                                     "https://en.wikipedia.org/wiki/Test"],
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        diprel = DiplomaticRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            references=["https://en.wikipedia.org/wiki/Test"],
            diplo_type='A',
        )
        diprel.parent_parties.add(new_PoliticalEntity)
        diprel.child_parties.add(child_PoliticalEntity)

    def test_api_can_create_PoliticalEntity(self):
        """
        Ensure we can create a new PoliticalEntity
        """
        url = reverse("politicalentity-list")
        data = {
            "name": "Created Test PoliticalEntity",
            "url_id": "created_test_PoliticalEntity",
            "color": "#ccffff",
            "references": ["https://en.wikipedia.org/wiki/Test"],
            'aliases': [],
            'links': []
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PoliticalEntity.objects.count(), 3)
        self.assertEqual(PoliticalEntity.objects.get(pk=3).name, "Created Test PoliticalEntity")

    def test_api_can_create_territory(self):
        """
        Ensure we can create a new territory
        """
        url = reverse("territory-list")
        data = {
            "start_date": "0006-01-01",
            "end_date": "0007-01-01",
            "entity": 'test_PoliticalEntity',
            'references': ["https://en.wikipedia.org/wiki/Test"],
            "geo": "{\"type\": \"MultiPolygon\",\"coordinates\": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Territory.objects.count(), 2)
        self.assertEqual(
            Territory.objects.get(pk=2).entity,
            PoliticalEntity.objects.get(pk=1)
        )

    def test_api_can_create_diprel(self):
        """
        Ensure we can create a new DiplomaticRelation
        """
        url = reverse("diplomaticrelation-list")
        data = {
            "start_date": "0001-01-01",
            "end_date": "0005-01-01",
            "references": [
                "https://en.wikipedia.org/wiki/Test"
            ],
            "parent_parties": [
                1
            ],
            "child_parties": [
                1
            ],
            "diplo_type": "A"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DiplomaticRelation.objects.count(), 2)
        self.assertEqual(DiplomaticRelation.objects.get(pk=2).diplo_type, 'A')

    def test_api_can_create_territory_FC(self):
        """
        Ensure we can create a new territory through
        a FeatureCollection
        """
        url = reverse("territory-list")
        data = {
            "start_date": "0008-01-01",
            "end_date": "0009-01-01",
            "entity": 'test_PoliticalEntity',
            'references': ["https://en.wikipedia.org/wiki/Test"],
            "geo": '{"type": "FeatureCollection","features": [{"type": "Feature","id": "id0","geometry": {"type": "Polygon","coordinates": [[[100,0],[101,0],[101,1],[100,1],[100,0]]]},"properties": {"prop0": "value0","prop1": "value1"}},{"type": "Feature","properties": {},"geometry": {"type": "Polygon","coordinates": [[[101.22802734375,-1.043643455908483],[102.601318359375,-2.2516174965491453],[102.864990234375,-0.36254640877525024],[101.22802734375,-1.043643455908483]]]}}]}'
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Territory.objects.count(), 2)
        self.assertEqual(
            Territory.objects.get(pk=3).entity,
            PoliticalEntity.objects.get(pk=1)
        )

    def test_api_can_update_territory(self):
        """
        Ensure we can update individual territories
        """
        url = reverse("territory-detail", args=[1])
        data = {
            "start_date": "0010-01-01",
            "end_date": "0011-01-01",
            "entity": 'test_PoliticalEntity',
            "geo": "{\"type\": \"MultiPolygon\",\"coordinates\": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["entity"], 'test_politicalentity')

    def test_api_can_update_PoliticalEntity(self):
        """
        Ensure we can update individual PoliticalEntitys
        """
        url = reverse("politicalentity-detail", args=["test_PoliticalEntity"])
        data = {
            "name": "Created Test PoliticalEntity",
            "url_id": "created_test_PoliticalEntity",
            "color": "#ccffff",
            "references": ["https://en.wikipedia.org/wiki/Test"],
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Created Test PoliticalEntity")

    def test_api_can_update_diprel(self):
        """
        Ensure we can update individual DipRels
        """
        url = reverse("diplomaticrelation-detail", args=[1])
        data = {
            "start_date": "0006-01-01",
            "end_date": "0010-01-01",
            "references": [
                "https://en.wikipedia.org/wiki/Test"
            ],
            "parent_parties": [
                1
            ],
            "child_parties": [
                1
            ],
            "diplo_type": "A"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['diplo_type'], 'A')

    def test_api_can_query_PoliticalEntitys(self):
        """
        Ensure we can query for all PoliticalEntitys
        """
        url = reverse("politicalentity-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Test PoliticalEntity")

    def test_api_can_query_territories(self):
        """
        Ensure we can query for all territories
        """
        url = reverse("territory-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["entity"], 1)

    def test_api_can_query_diprels(self):
        """
        Ensure we can query for all DipRels
        """
        url = reverse("diplomaticrelation-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['diplo_type'], 'A')

    def test_api_can_query_territories_bounds(self):
        """
        Ensure we can query for territories within a bounded
        region
        """
        url = reverse("territory-list") + \
            "?bounds=((0.0, 0.0), (0.0, 150.0), (150.0, 150.0), (150.0, 0.0), (0.0, 0.0))"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["entity"], 1)

    def test_api_can_not_query_territories_bounds(self):
        """
        Ensure querying for bounds in which the PoliticalEntity does not
        lie in fails
        """
        url = reverse("territory-list") + \
            "?bounds=((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(not response.data)

    def test_api_can_query_territories_date(self):
        """
        Ensure we can query for territories with a date
        """
        url = reverse("territory-list")+"?date=0001-01-01"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["entity"], 1)

    def test_api_can_not_query_territories_date(self):
        """
        Ensure querying for territories with an earlier start
        date fails
        """
        url = reverse("territory-list")+"?date=2020-01-01"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(not response.data)

    def test_api_can_query_PoliticalEntity(self):
        """
        Ensure we can query individual PoliticalEntitys
        """
        url = reverse("politicalentity-detail", args=["test_PoliticalEntity"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test PoliticalEntity")

    def test_api_can_query_territory(self):
        """
        Ensure we can query individual territories
        """
        url = reverse("territory-detail", args=[1])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["entity"], 1)

    def test_api_can_query_diprel(self):
        """
        Ensure we can query individual DipRels
        """
        url = reverse("diplomaticrelation-detail", args=[1])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["diplo_type"], 'A')
