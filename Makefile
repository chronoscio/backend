# import config
# You can change the default config with `make cnf="config_special.env" [command]`
cnf ?= django.env
include $(cnf)

# Documentation
.PHONY: help

help: ## Displays this message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# Docker tasks

pull: ## Pulls containers but does not start them
	docker-compose pull

build: ## Builds and tags containers
	docker-compose build

run: ## Builds, starts, and runs containers
	docker-compose up --build -d

stop: ## Stops running containers
	docker-compose stop

# Debug tools
run_debug: ## Builds, starts, and runs containers, running the built-in Django web server
	docker-compose run --service-ports web sh init.sh python manage.py runserver 0.0.0.0:81

exec_debug: ## Runs built-in Django web server
	docker-compose exec web python manage.py runserver 0.0.0.0:81

# Misc
test: ## Builds, starts, and runs containers, running the django tests
	docker-compose run --service-ports web sh init.sh python manage.py test

exec_test: ## Builds, starts, and runs containers, running the django tests
	docker-compose exec web python manage.py test

admin: ## Creates a super user in the running `web` container based on the values supplied in the configuration file [NOT WORKING ATM]
	docker-compose exec web ./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('$(ADMIN_USER)', '$(ADMIN_EMAIL)', '$(ADMIN_PASS)')"
