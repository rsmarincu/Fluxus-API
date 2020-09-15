#!/bin/bash

docker build --tag fluxuscontainerregistry.azurecr.io/pandas_api:latest .

docker push fluxuscontainerregistry.azurecr.io/pandas_api:latest