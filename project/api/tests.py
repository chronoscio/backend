from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Nation, Territory

# Create your tests here.
class APITest(APITestCase):

    @classmethod
    def setUpTestData(self):
        """
        Create basic model instances and test user
        """
        new_nation = Nation.objects.create(name="Test Nation",
                                           url_id="test_nation",
                                           color="fff",
                                           wikipedia="https://en.wikipedia.org/wiki/Test")
        Territory.objects.create(start_date="1444-11-11",
                                 end_date="2018-01-01",
                                 nation=new_nation,
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))
        User.objects.create_user("test_user", "test_email@example.com", "test_password")
        User.objects.create_superuser("test_admin", "test_admin_email@example.com", "test_password")

    def test_api_can_create_nation(self):
        """
        Ensure we can create a new nation
        """
        url = reverse("nation-list")
        data = {
            "name": "Created Test Nation",
            "url_id": "created_test_nation",
            "color": "#ccffff",
            "wikipedia": "https://en.wikipedia.org/wiki/Test"
        }
        token = Token.objects.get(user__username="test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
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
        token = Token.objects.get(user__username="test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Territory.objects.count(), 2)
        self.assertEqual(Territory.objects.get(pk=2).nation, Nation.objects.get(pk=1))


    def test_api_can_create_user(self):
        """
        Ensure we can create a new user
        """
        url = reverse("user-list")
        data = {
            "username": "created_test_user",
            "email": "created_test_user@example.com",
            "password": "test_password",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.get(pk=3).email, "created_test_user@example.com")
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
        token = Token.objects.get(user__username="test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nation"], 1)

    def test_api_can_update_nation(self):
        """
        Ensure we can query individual nations
        """
        url = reverse("nation-detail", args=["test_nation"])
        data = {
            "name": "Created Test Nation",
            "url_id": "created_test_nation",
            "color": "#ccffff",
            "wikipedia": "https://en.wikipedia.org/wiki/Test"
        }
        token = Token.objects.get(user__username="test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
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

    def test_api_can_not_query_users_nonadmin(self):
        """
        Ensure we can query for all users with adequate permissions
        """
        url = reverse("user-list")
        token = Token.objects.get(user__username="test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_can_not_query_passwords(self):
        """
        Ensure we can query for all users with adequate permissions
        """
        url = reverse("user-list")
        token = Token.objects.get(user__username="test_admin")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(url, format="json")
        with self.assertRaisesMessage(KeyError, "password"):
            response.data[0]["password"]

    def test_api_can_query_users_admin(self):
        """
        Ensure we can query for all users with adequate permissions
        """
        url = reverse("user-list")
        token = Token.objects.get(user__username="test_admin")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["email"], "test_email@example.com")

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

    def test_api_can_query_own_user(self):
        """
        Ensure users can access their data
        """
        url = reverse("user-detail", args=[1])
        token = Token.objects.get(user__username="test_user")
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test_email@example.com")

    def test_api_can_retrieve_token(self):
        """
        Ensure tokens can be retrieved for users
        """
        url = "/api-token-auth/"
        data = {
            "username": "test_user",
            "password": "test_password",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["token"], Token.objects.get(user__username="test_user").key)
