#!/bin/bash

docker build --tag fluxuscontainerregistry.azurecr.io/job-wq:latest  .

docker push fluxuscontainerregistry.azurecr.io/job-wq:latest