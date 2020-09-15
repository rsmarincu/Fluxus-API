#!/bin/bash

docker build --tag fluxuscontainerregistry.azurecr.io/visualisation_api:latest .

docker push fluxuscontainerregistry.azurecr.io/visualisation_api:latest