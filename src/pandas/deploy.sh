#!/bin/bash

docker build --tag fluxuscontainerregistry.azurecr.io/pandas-api:latest .

docker push fluxuscontainerregistry.azurecr.io/pandas-api:latest