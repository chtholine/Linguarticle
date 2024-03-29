.PHONY: d-run
# Just run
d-run:
	@COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 \
		COMPOSE_PROFILES=full_dev \
		docker compose \
			up --build

.PHONY: d-run-local-dev
# Just run
d-run-local-dev:
	@COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 \
		COMPOSE_PROFILES=local_dev \
		docker compose \
			up --build -d && \
	docker-compose logs -f postgres & \
	python manage.py runserver

.PHONY: d-purge
# Purge all data related with services
d-purge:
	@COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 \
		docker compose \
			down --volumes --remove-orphans --rmi local --timeout 0

.PHONY: pre-commit-run
# Run tools for files from commit.
pre-commit-run:
	@pre-commit run

.PHONY: pre-commit-run-all
# Run tools for all files.
pre-commit-run-all:
	@pre-commit run --all-files

.PHONY: util-i-kill-by-port
util-i-kill-by-port:
	@sudo lsof -i:5432 -Fp | head -n 1 | sed 's/^p//' | xargs sudo kill