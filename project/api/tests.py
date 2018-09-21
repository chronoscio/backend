import json
import requests

from django.urls import reverse
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase
from os import environ

from .models import Nation, Territory, DiplomaticRelation

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
def getUserToken(client_id=environ['AUTH0_CLIENT_ID'], client_secret=environ['AUTH0_CLIENT_SECRET']):
    url = 'https://' + environ['AUTH0_DOMAIN'] + '/oauth/token'
    headers = {'content-type': 'application/json'}
    parameter = {"client_id": client_id,
                 'client_secret': client_secret,
                 "audience": environ['API_IDENTIFIER'],
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
        new_nation = Nation.objects.create(name="Test Nation",
                                           url_id="test_nation",
                                           color="fff",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        new_nation.save()

        child_nation = Nation.objects.create(name="Test Child Nation",
                                           url_id="test_child_nation",
                                           color="ccc",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        child_nation.save()
        Territory.objects.create(start_date="1444-11-11",
                                 end_date="2018-01-01",
                                 nation=new_nation,
                                 references=[
                                     "https://en.wikipedia.org/wiki/Test"],
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        diprel = DiplomaticRelation.objects.create(
            start_date="1444-11-11",
            end_date="2018-01-01",
            references=["https://en.wikipedia.org/wiki/Test"],
            diplo_type='A',
        )
        diprel.parent_parties.add(new_nation)
        diprel.child_parties.add(child_nation)

    def test_model_can_create_nation(self):
        """
        Ensure that we can create nations.
        """
        new_nation = Nation.objects.create(name="Test Nation2",
                                           url_id="test_nation2",
                                           color="ddd",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        new_nation.save()
        self.assertTrue(Nation.objects.filter(url_id="test_nation2").exists())

    def test_model_can_create_territory(self):
        """
        Ensure that we can create territories.
        """
        nation = Nation.objects.get(url_id="test_nation")
        Territory.objects.create(start_date="2018-01-05",
                                 end_date="2018-01-07",
                                 nation=nation,
                                 references=[
                                     "https://en.wikipedia.org/wiki/Test"],
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        
        Territory.objects.create(start_date="2018-01-02",
                                 end_date="2018-01-04",
                                 nation=nation,
                                 references=[
                                     "https://en.wikipedia.org/wiki/Test"],
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        

        self.assertTrue(Territory.objects.filter(nation = nation,start_date = "2018-01-02",end_date = "2018-01-04").exists())

    def test_model_cant_create_territory(self):
        """
        Ensure that date checks work.
        """
        new_nation = Nation.objects.get(url_id="test_nation")
        with self.assertRaises(ValidationError):
            Territory.objects.create(start_date="1444-11-11",
                                     end_date="2010-01-01",
                                     nation=new_nation,
                                     references=[
                                         "https://en.wikipedia.org/wiki/Test"],
                                     geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))


class APITest(APITestCase):

    @classmethod
    def setUpTestData(self):
        """
        Create basic model instances and test user
        """
        new_nation=Nation.objects.create(name="Test Nation",
                                           url_id="test_nation",
                                           color="fff",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        new_nation.save()
        child_nation=Nation.objects.create(name="Test Child Nation",
                                           url_id="test_child_nation",
                                           color="ccc",
                                           references=[
                                               "https://en.wikipedia.org/wiki/Test"],
                                           aliases=[],
                                           links=[])
        child_nation.save()
        Territory.objects.create(start_date="1444-11-11",
                                 end_date="2018-01-01",
                                 nation=new_nation,
                                 references=[
                                     "https://en.wikipedia.org/wiki/Test"],
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        diprel=DiplomaticRelation.objects.create(
            start_date="1444-11-11",
            end_date="2018-01-01",
            references=["https://en.wikipedia.org/wiki/Test"],
            diplo_type='A',
        )
        diprel.parent_parties.add(new_nation)
        diprel.child_parties.add(child_nation)

    def test_api_can_create_nation(self):
        """
        Ensure we can create a new nation
        """
        url=reverse("nation-list")
        data={
            "name": "Created Test Nation",
            "url_id": "created_test_nation",
            "color": "#ccffff",
            "references": ["https://en.wikipedia.org/wiki/Test"],
            'aliases': [],
            'links': []
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response=self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Nation.objects.count(), 3)
        self.assertEqual(Nation.objects.get(pk=3).name, "Created Test Nation")

    def test_api_can_create_territory(self):
        """
        Ensure we can create a new territory
        """
        url=reverse("territory-list")
        data={
            "start_date": "2018-02-02",
            "end_date": "2018-02-03",
            "nation": 1,
            'references': ["https://en.wikipedia.org/wiki/Test"],
            "geo": "{\"type\": \"MultiPolygon\",\"coordinates\": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response=self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Territory.objects.count(), 2)
        self.assertEqual(
            Territory.objects.get(pk=2).nation,
            Nation.objects.get(pk=1)
        )

    def test_api_can_create_diprel(self):
        """
        Ensure we can create a new DiplomaticRelation
        """
        url=reverse("diplomaticrelation-list")
        data={
            "start_date": "2010-07-20",
            "end_date": "2018-07-20",
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
        response=self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DiplomaticRelation.objects.count(), 2)
        self.assertEqual(DiplomaticRelation.objects.get(pk=2).diplo_type, 'A')

    def test_api_can_create_territory_FC(self):
        """
        Ensure we can create a new territory through
        a FeatureCollection
        """
        url=reverse("territory-list")
        data={
            "start_date": "2018-03-03",
            "end_date": "2018-03-04",
            "nation": 1,
            'references': ["https://en.wikipedia.org/wiki/Test"],
            "geo": '{"type": "FeatureCollection","features": [{"type": "Feature","id": "id0","geometry": {"type": "Polygon","coordinates": [[[100,0],[101,0],[101,1],[100,1],[100,0]]]},"properties": {"prop0": "value0","prop1": "value1"}},{"type": "Feature","properties": {},"geometry": {"type": "Polygon","coordinates": [[[101.22802734375,-1.043643455908483],[102.601318359375,-2.2516174965491453],[102.864990234375,-0.36254640877525024],[101.22802734375,-1.043643455908483]]]}}]}'
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response=self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Territory.objects.count(), 2)
        self.assertEqual(
            Territory.objects.get(pk=3).nation,
            Nation.objects.get(pk=1)
        )

    def test_api_can_update_territory(self):
        """
        Ensure we can update individual territories
        """
        url=reverse("territory-detail", args=[1])
        data={
            "start_date": "2018-04-04",
            "end_date": "2018-04-05",
            "nation": 1,
            "geo": "{\"type\": \"MultiPolygon\",\"coordinates\": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response=self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nation"], 1)

    def test_api_can_update_nation(self):
        """
        Ensure we can update individual nations
        """
        url=reverse("nation-detail", args=["test_nation"])
        data={
            "name": "Created Test Nation",
            "url_id": "created_test_nation",
            "color": "#ccffff",
            "references": ["https://en.wikipedia.org/wiki/Test"],
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response=self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Created Test Nation")

    def test_api_can_update_diprel(self):
        """
        Ensure we can update individual DipRels
        """
        url=reverse("diplomaticrelation-detail", args=[1])
        data={
            "start_date": "2010-07-20",
            "end_date": "2018-07-20",
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
        response=self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['diplo_type'], 'A')

    def test_api_can_query_nations(self):
        """
        Ensure we can query for all nations
        """
        url=reverse("nation-list")
        response=self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Test Nation")

    def test_api_can_query_territories(self):
        """
        Ensure we can query for all territories
        """
        url=reverse("territory-list")
        response=self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["nation"], 1)

    def test_api_can_query_diprels(self):
        """
        Ensure we can query for all DipRels
        """
        url=reverse("diplomaticrelation-list")
        response=self.client.get(url, format="json")
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
        self.assertEqual(response.data[0]["nation"], 1)

    def test_api_can_not_query_territories_bounds(self):
        """
        Ensure querying for bounds in which the nation does not
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
        url = reverse("territory-list")+"?date=2011-01-1"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["nation"], 1)

    def test_api_can_not_query_territories_date(self):
        """
        Ensure querying for territories with an earlier start
        date fails
        """
        url = reverse("territory-list")+"?date=2020-01-01"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(not response.data)

    def test_api_can_query_nation(self):
        """
        Ensure we can query individual nations
        """
        url = reverse("nation-detail", args=["test_nation"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Nation")

    def test_api_can_query_territory(self):
        """
        Ensure we can query individual territories
        """
        url = reverse("territory-detail", args=[1])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nation"], 1)

    def test_api_can_query_diprel(self):
        """
        Ensure we can query individual DipRels
        """
        url = reverse("diplomaticrelation-detail", args=[1])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["diplo_type"], 'A')
