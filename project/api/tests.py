from django.test import TestCase, RequestFactory
from django.contrib.gis.geos import GEOSGeometry
from graphene.test import Client

from .schema import SCHEMA
from .models import *

def execute_test_client_api_query(api_query, user=None, variable_values=None, **kwargs):
    """
    Returns the results of executing a graphQL query using the graphene test client.  This is a helper method for our tests
    """
    request_factory = RequestFactory()
    context_value = request_factory.get('/api/')
    context_value.user = user
    client = Client(SCHEMA)
    executed = client.execute(api_query, context_value=context_value, variable_values=variable_values, **kwargs)
    return executed

# Create your tests here.
class APITest(TestCase):
    @classmethod
    def setUpTestData(self):
        new_nation = Nation.objects.create(name="Test Nation",
                              local_name="Test Nation",
                              wikipedia="https://en.wikipedia.org/wiki/Test")
        Territory.objects.create(start_date="1444-11-11",
                              end_date="2018-01-01",
                              nation=new_nation,
                              geo=GEOSGeometry('{"type":"Polygon","coordinates":[[[-6.0, 40.0],[-5.0, 40.0],[-5.0, 38.0],[-7.0, 37.0],[-6.0, 40.0]]]}'))

    def test_graphql_can_create_nation(self):
        query = '''
                mutation CreateNation($input: CreateNationInput!) {
                    createNation(input: $input) {
                        newNation {
                            name
                            localName
                            wikipedia
                            id
                        }
                    }
                }
                '''
        variable_values = {
                            "input": {
                                "nation": {
                                   "name": "Test Nation",
                                   "localName": "\u30b5\u30f3\u30d7\u30eb\u30c7\u30fc\u30bf",
                                   "wikipedia": "https://en.wikipedia.org/wiki/Test"
                                }
                            }
                          }
        executed = execute_test_client_api_query(query, variable_values=variable_values)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['createNation']['newNation']['name'], 'Test Nation')

    def test_graphql_can_create_territory(self):
        query = '''
                mutation CreateTerritory($input: CreateTerritoryInput!) {
                    createTerritory(input: $input) {
                        newTerritory {
                            startDate
                            endDate
                            geo
                            nation {
                                id
                            }
                        }
                        clientMutationId
                    }
                }
                '''
        variable_values = {
                            "input": {
                                "territory": {
                                    "startDate": "2010-07-20",
                                    "endDate": "2018-07-20",
                                    "nation": 1,
                                    "geo": "{\"type\":\"Polygon\",\"coordinates\":[[[-6.0, 40.0],[-5.0, 40.0],[-5.0, 38.0],[-7.0, 37.0],[-6.0, 40.0]]]}"
                                }
                            }
                          }
        executed = execute_test_client_api_query(query, variable_values=variable_values)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['createTerritory']['newTerritory']['geo']['type'], 'Polygon')

    def test_graphql_can_query_nations(self):
        query = '''
                {
                    nations {
                        name
                    }
                }
                '''
        executed = execute_test_client_api_query(query)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['nations'][0]['name'], 'Test Nation')

    def test_graphql_can_query_territories(self):
        query = '''
                {
                    territories {
                        nation {
                            name
                        }
                    }
                }
                '''
        executed = execute_test_client_api_query(query)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['territories'][0]['nation']['name'], 'Test Nation')
