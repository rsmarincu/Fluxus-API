#!/bin/bash

docker build --tag fluxuscontainerregistry.azurecr.io/compute:latest .

docker push fluxuscontainerregistry.azurecr.io/compute:latest