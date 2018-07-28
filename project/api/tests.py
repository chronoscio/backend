from django.test import TestCase, RequestFactory
from django.contrib.gis.geos import GEOSGeometry
from graphene.test import Client

from .schema import schema
from .models import *

def execute_test_client_api_query(api_query, user=None, variable_values=None, **kwargs):
    """
    Returns the results of executing a graphQL query using the graphene test client.  This is a helper method for our tests
    """
    request_factory = RequestFactory()
    context_value = request_factory.get('/graphql/')
    context_value.user = user
    client = Client(schema)
    executed = client.execute(api_query, context_value=context_value, variable_values=variable_values, **kwargs)
    return executed

# Create your tests here.
class APITest(TestCase):
    @classmethod
    def setUpTestData(self):
        new_nation = Nation.objects.create(name="Test Nation",
                                           color="fff",
                                           wikipedia="https://en.wikipedia.org/wiki/Test")
        Territory.objects.create(start_date="1444-11-11",
                                 end_date="2018-01-01",
                                 nation=new_nation,
                                 geo=GEOSGeometry('{"type": "MultiPolygon","coordinates": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}'))

    def test_graphql_can_create_nation(self):
        query = '''
                mutation CreateNation($input: CreateNationInput!) {
                    createNation(input: $input) {
                        newNation {
                            name
                            color
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
                                   "color": "fff",
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
                                    "geo": "{\"type\": \"MultiPolygon\",\"coordinates\": [[[ [102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0] ]],[[ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ],[ [100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2] ]]]}"
                                }
                            }
                          }
        executed = execute_test_client_api_query(query, variable_values=variable_values)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['createTerritory']['newTerritory']['geo']['type'], 'MultiPolygon')

    def test_graphql_can_query_nations(self):
        query = '''
                {
                    allNations {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
                '''
        executed = execute_test_client_api_query(query)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['allNations']['edges'][0]['node']['name'], 'Test Nation')

    def test_graphql_can_query_territories(self):
        query = '''
                {
                    allTerritories {
                        edges {
                            node {
                                id
                                nation {
                                    name
                                }
                            }
                        }
                    }
                }
                '''
        executed = execute_test_client_api_query(query)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['allTerritories']['edges'][0]['node']['nation']['name'], 'Test Nation')

    def test_graphql_can_query_nation(self):
        query = '''
                {
                    nation (id: "TmF0aW9uOjE=") {
                        name
                    }
                }
                '''
        executed = execute_test_client_api_query(query)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['nation']['name'], 'Test Nation')

    def test_graphql_can_query_territory(self):
        query = '''
                {
                    territory (id: "VGVycml0b3J5OjE=") {
                        nation {
                            name
                        }
                    }
                }
                '''
        executed = execute_test_client_api_query(query)
        data = executed.get('data')
        print(data)
        self.assertEqual(data['territory']['nation']['name'], 'Test Nation')
