import json
import requests

from django.conf import settings
from django.urls import reverse
from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework import status
import geobuf
from rest_framework.test import APITestCase
from .models import PoliticalEntity, Territory, DiplomaticRelation
from .factories import (
    PoliticalEntityFactory,
    TerritoryFactory,
    DiplomaticRelationFactory,
)

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
def getUserToken(
    client_id=settings.AUTH0_CLIENT_ID, client_secret=settings.AUTH0_CLIENT_SECRET
):
    url = "https://" + settings.AUTH0_DOMAIN + "/oauth/token"
    headers = {"content-type": "application/json"}
    parameter = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": settings.API_IDENTIFIER,
        "grant_type": "client_credentials",
    }
    response = json.loads(requests.post(url, json=parameter, headers=headers).text)
    return response["access_token"]


class ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Create basic model instances and test user
        """
        cls.new_nation = PoliticalEntityFactory(
            name="Test Nation",
            url_id="test_nation",
            color="fff",
            references=["https://en.wikipedia.org/wiki/Test"],
            aliases=[],
            links=[],
        )

        cls.child_nation = PoliticalEntityFactory(
            name="Test Child Nation",
            url_id="test_child_nation",
            color="ccc",
            references=["https://en.wikipedia.org/wiki/Test"],
            aliases=[],
            links=[],
        )
        cls.territory = TerritoryFactory(
            start_date="0002-01-01",
            end_date="0004-01-01",
            entity=cls.new_nation,
            references=["https://en.wikipedia.org/wiki/Test"],
            geo=GEOSGeometry(
                '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'
            ),
        )
        cls.diprel = DiplomaticRelationFactory(
            start_date="0001-01-01",
            end_date="0005-01-01",
            references=["https://en.wikipedia.org/wiki/Test"],
            diplo_type="A",
        )
        cls.diprel.parent_parties.add(cls.new_nation)
        cls.diprel.child_parties.add(cls.child_nation)

    def test_model_can_create_politicalentity(self):
        """
        Ensure that we can create politicalentities.
        """
        new_politicalentity = PoliticalEntity.objects.create(
            name="Test Nation2",
            url_id="test_nation2",
            color="ddd",
            references=["https://en.wikipedia.org/wiki/Test"],
            aliases=[],
            links=[],
        )
        new_politicalentity.save()
        self.assertTrue(PoliticalEntity.objects.filter(url_id="test_nation2").exists())

    def test_model_can_create_territory(self):
        """
        Ensure that we can create territories. Specifically checks if we can create [start_date+1,end_date-1]
        """
        politicalentity = PoliticalEntity.objects.get(url_id="test_nation")
        Territory.objects.create(
            start_date="0007-01-01",
            end_date="0008-01-01",
            entity=politicalentity,
            references=["https://en.wikipedia.org/wiki/Test"],
            geo=GEOSGeometry(
                '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'
            ),
        )
        self.assertTrue(
            Territory.objects.filter(
                entity=politicalentity, start_date="0007-01-01", end_date="0008-01-01"
            ).exists()
        )
        politicalentity = PoliticalEntity.objects.get(url_id="test_nation")
        Territory.objects.create(
            start_date="0004-01-02",
            end_date="0006-12-31",
            entity=politicalentity,
            references=["https://en.wikipedia.org/wiki/Test"],
            geo=GEOSGeometry(
                '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'
            ),
        )
        self.assertTrue(
            Territory.objects.filter(
                entity=politicalentity, start_date="0004-01-02", end_date="0006-12-31"
            ).exists()
        )

    def test_model_can_not_create_territory(self):
        """
        Ensure that date checks work.
        """
        new_politicalentity = PoliticalEntity.objects.get(url_id="test_nation")
        with self.assertRaises(ValidationError):
            Territory.objects.create(
                start_date="0001-01-01",
                end_date="0003-01-01",
                entity=new_politicalentity,
                references=["https://en.wikipedia.org/wiki/Test"],
                geo=GEOSGeometry(
                    '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'
                ),
            )
        with self.assertRaises(ValidationError):
            Territory.objects.create(
                start_date="0002-01-01",
                end_date="0003-01-01",
                entity=new_politicalentity,
                references=["https://en.wikipedia.org/wiki/Test"],
                geo=GEOSGeometry(
                    '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'
                ),
            )
        with self.assertRaises(ValidationError):
            Territory.objects.create(
                start_date="0003-01-01",
                end_date="0005-01-01",
                entity=new_politicalentity,
                references=["https://en.wikipedia.org/wiki/Test"],
                geo=GEOSGeometry(
                    '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'
                ),
            )
        with self.assertRaises(ValidationError):
            Territory.objects.create(
                start_date="0001-01-01",
                end_date="0005-01-01",
                entity=new_politicalentity,
                references=["https://en.wikipedia.org/wiki/Test"],
                geo=GEOSGeometry(
                    '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'
                ),
            )


class APITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Create basic model instances
        """
        cls.new_nation = PoliticalEntityFactory(
            name="Test Nation",
            url_id="test_nation",
            color="fff",
            references=["https://en.wikipedia.org/wiki/Test"],
            aliases=[],
            links=[],
        )
        cls.child_nation = PoliticalEntityFactory(
            name="Test Child Nation",
            url_id="test_child_nation",
            color="ccc",
            references=["https://en.wikipedia.org/wiki/Test"],
            aliases=[],
            links=[],
        )
        cls.territory = TerritoryFactory(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=cls.new_nation,
            references=["https://en.wikipedia.org/wiki/Test"],
            geo=GEOSGeometry(
                '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'
            ),
        )
        cls.territory2 = TerritoryFactory(
            start_date="0030-01-02",
            end_date="0035-01-01",
            entity=cls.new_nation,
            references=["https://en.wikipedia.org/wiki/Test"],
            geo=GEOSGeometry(
                '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ]]]}'
            ),
        )
        cls.diprel = DiplomaticRelationFactory(
            start_date="0001-01-01",
            end_date="0005-01-01",
            references=["https://en.wikipedia.org/wiki/Test"],
            diplo_type="A",
        )
        cls.diprel.parent_parties.add(cls.new_nation)
        cls.diprel.child_parties.add(cls.child_nation)

    def test_api_can_create_PoliticalEntity(self):
        """
        Ensure we can create a new PoliticalEntity
        """
        url = reverse("politicalentity-list")
        data = {
            "name": "Created Test Nation",
            "url_id": "created_test_nation",
            "color": "#ccffff",
            "references": ["https://en.wikipedia.org/wiki/Test"],
            "aliases": [],
            "links": [],
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PoliticalEntity.objects.count(), 3)
        self.assertEqual(PoliticalEntity.objects.get(pk=3).name, "Created Test Nation")

    def test_api_can_create_territory_FC(self):
        """
        Ensure we can create a new territory through
        a FeatureCollection
        """
        url = reverse("territory-list")
        data = {
            "start_date": "0008-01-01",
            "end_date": "0009-01-01",
            "entity": self.new_nation.id,
            "references": ["https://en.wikipedia.org/wiki/Test"],
            "geo": '{"type": "FeatureCollection","features": [{"type": "Feature","id": "id0","geometry": {"type": "Polygon","coordinates": [[[100,0],[101,0],[101,1],[100,1],[100,0]]]},"properties": {"prop0": "value0","prop1": "value1"}},{"type": "Feature","properties": {},"geometry": {"type": "Polygon","coordinates": [[[101.22802734375,-1.043643455908483],[102.601318359375,-2.2516174965491453],[102.864990234375,-0.36254640877525024],[101.22802734375,-1.043643455908483]]]}}]}',
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Territory.objects.count(), 3)
        self.assertEqual(Territory.objects.last().entity, self.new_nation)

    def test_api_can_create_territory(self):
        """
        Ensure we can create a new territory
        """
        url = reverse("territory-list")
        data = {
            "start_date": "0006-01-01",
            "end_date": "0007-01-01",
            "entity": self.new_nation.id,
            "references": ["https://en.wikipedia.org/wiki/Test"],
            "geo": '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}',
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Territory.objects.count(), 3)
        self.assertEqual(Territory.objects.last().entity, self.new_nation)

    def test_api_can_update_PoliticalEntity(self):
        """
        Ensure we can update individual PoliticalEntities
        """
        url = reverse("politicalentity-detail", args=["test_nation"])
        data = {
            "name": "Created Test Nation",
            "url_id": "created_test_nation",
            "color": "#ccffff",
            "references": ["https://en.wikipedia.org/wiki/Test"],
            "geo": '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}',
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Created Test Nation")

    def test_api_can_update_territory(self):
        """
        Ensure we can update individual territories
        """
        url = reverse("territory-detail", args=[self.territory.id])
        data = {
            "start_date": "0010-01-01",
            "end_date": "0011-01-01",
            "entity": self.child_nation.id,
            "geo": '{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}',
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["entity"], self.child_nation.url_id)

    def test_api_can_query_PoliticalEntities(self):
        """
        Ensure we can query for all PoliticalEntities
        """
        url = reverse("politicalentity-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], "Test Nation")

    def test_api_can_query_territories(self):
        """
        Ensure we can query for all territories
        """
        url = reverse("territory-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["entity"], "test_nation")

    def test_api_can_decompress_geojson(self):
        """
        Ensure we send geometry as a valid geobuf.
        """
        url = reverse("territory-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        gbuf = bytes.fromhex(response.data[0]["geo"])
        geojson = json.dumps(geobuf.decode(gbuf))
        self.assertEqual(
            geojson,
            '{"type": "MultiPolygon", "coordinates": [[[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]], [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]], [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]]}',
        )

    def test_api_can_query_territory(self):
        """
        Ensure we can query individual territories
        """
        url = reverse("territory-detail", args=[self.territory.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["entity"], "test_nation")

    def test_api_can_query_territories_bounds(self):
        """
        Ensure we can query for territories within a bounded
        region
        """
        url = (
            reverse("territory-list")
            + "?bounds=((0.0, 0.0), (0.0, 150.0), (150.0, 150.0), (150.0, 0.0), (0.0, 0.0))"
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["entity"], "test_nation")

    def test_api_can_not_query_territories_bounds(self):
        """
        Ensure querying for bounds in which the PoliticalEntity does not
        lie in fails
        """
        url = (
            reverse("territory-list")
            + "?bounds=((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0))"
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(not response.data)

    def test_api_can_query_territories_date(self):
        """
        Ensure we can query for territories with a date
        """
        url = reverse("territory-list") + "?date=0001-01-01"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["entity"], "test_nation")

    def test_api_can_not_query_territories_date(self):
        """
        Ensure querying for territories with an earlier start
        date fails
        """
        url = reverse("territory-list") + "?date=2020-01-01"
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(not response.data)

    def test_api_can_query_PoliticalEntity(self):
        """
        Ensure we can query individual PoliticalEntities
        """
        url = reverse("politicalentity-detail", args=["test_nation"])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Nation")

    def test_api_can_query_territories_exclude(self):
        """
        Ensure we can exclude territories by id
        """
        url = reverse("territory-list") + "?exclude_ids=" + str(self.territory.id)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.territory2.id)
        response = self.client.get(url + "," + str(self.territory2.id))
        self.assertTrue(not response.data)

    def test_api_can_create_diprel(self):
        """
        Ensure we can create a new DiplomaticRelation
        """
        url = reverse("diplomaticrelation-list")
        data = {
            "start_date": "0001-01-01",
            "end_date": "0005-01-01",
            "references": ["https://en.wikipedia.org/wiki/Test"],
            "parent_parties": [self.new_nation.id],
            "child_parties": [self.child_nation.id],
            "diplo_type": "A",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DiplomaticRelation.objects.count(), 2)
        self.assertEqual(DiplomaticRelation.objects.last().diplo_type, "A")

    def test_api_can_update_diprel(self):
        """
        Ensure we can update individual DipRels
        """
        url = reverse("diplomaticrelation-detail", args=[self.diprel.id])
        data = {
            "start_date": "0006-01-01",
            "end_date": "0010-01-01",
            "references": ["https://en.wikipedia.org/wiki/Test"],
            "parent_parties": [self.new_nation.id],
            "child_parties": [self.new_nation.id],
            "diplo_type": "A",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + getUserToken())
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["diplo_type"], "A")

    def test_api_can_query_diprels(self):
        """
        Ensure we can query for all DipRels
        """
        url = reverse("diplomaticrelation-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["diplo_type"], "A")

    def test_api_can_query_diprel(self):
        """
        Ensure we can query individual DipRels
        """
        url = reverse("diplomaticrelation-detail", args=[self.diprel.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["diplo_type"], "A")
