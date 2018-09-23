# Building ChronoScio Backend

Note: this document is still in a draft state, ideas are for now just thrown
out one after the other. As the project grows, the organization of this
document should be perfected as well.

## Django

This project uses [django](https://www.djangoproject.com/), please refer to
their doc to learn on how it works roughly.

Most classes have descriptive docstrings, check code for more information about specific blocks,
or feel free to ask on the [Discord server](https://discord.gg/mmRAeEB).

### Application Structure

All code is in the `project/` directory. The base app is `interactivemap/`
and most code is located in the `api/` app, which uses
[Django REST Framework](http://www.django-rest-framework.org/). Previous versions
of the repository used graphene-django as a GraphQl server.

The `config/` folder contains the nginx configuration and a pip `requirements.txt`.

### Authentication

Very minimal user information is stored on the backend. Additionally, the frontend does
not call the backend to retrieve or interact with any users. This is all handled via Auth0,
which provides us with a stateless JWT which can be validated through their servers. An
[access token](https://auth0.com/docs/tokens/access-token) is required to be passed to the
backend

### Database

[PostgreSQL](https://www.postgresql.org/) is the primary database backend for this project. The
[PostGIS](https://postgis.net/) extension is additionally used to perform spatial relation tasks,
and the [djangorestframework-gis](https://github.com/djangonauts/django-rest-framework-gis) package
is used to allow it to play nice with DRF.

## Docker and Makefile

The project itself uses [docker-compose](https://docs.docker.com/compose/) which is
principally interacted with via a `Makefile`. Running `make` or `make help` will print
a documented list of all available commands and shortcuts to help with development, so
a nuanced understanding of docker is not necessary for code contribution.

## API endpoints

```bash
$ curl --request GET   --url http://localhost/api/    --header 'athorization: Bearer {ACCESS_TOKEN}'
{
    "nations": "http://web/api/nations/",
    "territories": "http://web/api/territories/"
}
```

## Obtaining Test Data

```bash
# Import:
mv docs/example_db_dump.json project/db.json # optional, uses our provided test data
docker-compose exec web python manage.py loaddata db.json # note that this will assume db.json is in the project directory

# Export:
docker-compose exec web python manage.py dumpdata \
  --natural-foreign --exclude auth.permission --exclude contenttypes \
  > db.json
```
