#!make
include .env

##################### Initializing | needs run once at project start

# Initializing Git
initialize_git:
	@echo "Initializing git..."
	git init

# Installing Poetry
install: 
	@echo "Installing..."
	poetry install

activate_precommit:
	poetry run pre-commit install

# Enable required GCP services
enable_gcp_services:
	@echo "Enabling GCP services..."
	gcloud services enable iamcredentials.googleapis.com
	gcloud services enable artifactregistry.googleapis.com
	gcloud services enable run.googleapis.com
	gcloud services enable compute.googleapis.com

# Setup GCP Project, create Service account(s) and add policies
setup_gcp_project:
# @echo "Creating GCP service account..."
# gcloud projects delete $(CLOUDSDK_CORE_PROJECT)
# gcloud projects create $(CLOUDSDK_CORE_PROJECT)
# gcloud iam service-accounts create $(GCP_SA_NAME)
	gcloud projects add-iam-policy-binding $(CLOUDSDK_CORE_PROJECT) --member=$(MEMBER) --role="roles/run.admin"
	gcloud projects add-iam-policy-binding $(CLOUDSDK_CORE_PROJECT) --member=$(MEMBER) --role="roles/compute.instanceAdmin.v1"
	gcloud projects add-iam-policy-binding $(CLOUDSDK_CORE_PROJECT) --member=$(MEMBER) --role="roles/artifactregistry.admin"
	gcloud projects add-iam-policy-binding $(CLOUDSDK_CORE_PROJECT) --member=$(MEMBER) --role="roles/iam.serviceAccountUser"
	gcloud projects add-iam-policy-binding $(CLOUDSDK_CORE_PROJECT) --member=$(MEMBER) --role="roles/storage.objectAdmin"

setup_gcp_service_account:
	@echo "Creating GCP service account keyfile..."
	gcloud iam service-accounts keys create credentials/prefect_service_account.json --iam-account="$(GCP_SA_NAME)@$(CLOUDSDK_CORE_PROJECT).iam.gserviceaccount.com"

##################### Startup | needs run everytime you open the Command line


# Activate Virtual Env
activate:
	@echo "Activating virtual environment"
	poetry shell

##################### Testing functions | needs to run before committing new functions

test:
	pytest

##################### Database Structure changes

sql2dbml:
	sql2dbml --mysql schema/prod/instagram_db.sql -o schema/prod/instagram_db.dbml

dbml2sql:
	dbml2sql --mysql schema/prod/instagram_db.dbml -o schema/prod/instagram_db.sql

##################### Deployment

export_dependencies:
	poetry export -o "requirements.txt" --without-hashes --without-urls

build_docker_image:
# gcloud artifacts repositories create prefect-flows --location=$(CLOUDSDK_COMPUTE_REGION) --repository-format="DOCKER"
	docker build -t $(CLOUDSDK_COMPUTE_REGION)-docker.pkg.dev/$(CLOUDSDK_CORE_PROJECT)/prefect-flows/$(HEALTHCHECK_FLOW_NAME):$(PREFECT_IMAGE_VERSION)-python$(PYTHON_VERSION) .
	gcloud auth configure-docker $(CLOUDSDK_COMPUTE_REGION)-docker.pkg.dev
	docker push $(CLOUDSDK_COMPUTE_REGION)-docker.pkg.dev/$(CLOUDSDK_CORE_PROJECT)/prefect-flows/$(HEALTHCHECK_FLOW_NAME):$(PREFECT_IMAGE_VERSION)-python$(PYTHON_VERSION)

##################### Documentation

docs_view:
	@echo View API documentation... 
	PYTHONPATH=src pdoc src --http localhost:8080

docs_save:
	@echo Save documentation to docs... 
	PYTHONPATH=src pdoc src -o docs


##################### Clean up

# Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache