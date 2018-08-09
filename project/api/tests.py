from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from rest_framework import status
from rest_framework.test import APITestCase

from .models import *

# Create your tests here.
class APITest(APITestCase):

    @classmethod
    def setUpTestData(self):
        """
        Create basic model instances
        """
        new_nation = Nation.objects.create(name="Test Nation",
                                           color="fff",
                                           wikipedia="https://en.wikipedia.org/wiki/Test")
        Territory.objects.create(start_date="1444-11-11",
                                 end_date="2018-01-01",
                                 nation=new_nation,
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        User.objects.create_user("test_user", "test_email@example.com", "test_password")

    def test_api_can_create_nation(self):
        """
        Ensure we can create a new nation
        """
        url = reverse("nation-list")
        data = {
            "name": "Created Test Nation",
            "color": "#ccffff",
            "wikipedia": "https://en.wikipedia.org/wiki/Test"
        }
        self.client.login(username="test_user", password="test_password")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Nation.objects.count(), 2)
        self.assertEqual(Nation.objects.get(pk=2).name, "Created Test Nation")

    def test_api_can_create_territory(self):
        """
        Ensure we can create a new territory
        """
        url = reverse("territory-list")
        data = {
            "start_date": "2010-07-20",
            "end_date": "2018-07-20",
            "nation": 1,
            "geo": "{\"type\": \"MultiPolygon\",\"coordinates\": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}"
        }
        self.client.login(username="test_user", password="test_password")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Territory.objects.count(), 2)
        self.assertEqual(Territory.objects.get(pk=2).nation, Nation.objects.get(pk=1))

    def test_api_can_update_territory(self):
        """
        Ensure we can query individual territories
        """
        url = reverse("territory-detail", args=[1])
        data = {
            "start_date": "2010-07-20",
            "end_date": "2018-07-20",
            "nation": 1,
            "geo": "{\"type\": \"MultiPolygon\",\"coordinates\": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}"
        }
        self.client.login(username="test_user", password="test_password")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nation"], 1)

    def test_api_can_update_nation(self):
        """
        Ensure we can query individual nations
        """
        url = reverse("nation-detail", args=[1])
        data = {
            "name": "Created Test Nation",
            "color": "#ccffff",
            "wikipedia": "https://en.wikipedia.org/wiki/Test"
        }
        self.client.login(username="test_user", password="test_password")
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Created Test Nation")

    def test_api_can_query_nations(self):
        """
        Ensure we can query for all nations
        """
        url = reverse("nation-list")
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
        self.assertEqual(response.data[0]["nation"], 1)

    def test_api_can_query_nation(self):
        """
        Ensure we can query individual nations
        """
        url = reverse("nation-detail", args=[1])
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
