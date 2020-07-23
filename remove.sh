#!/bin/bash

kubectl delete service neo4j-lb graphql math-api pandas-api reverse-proxy visualisation-api

kubectl delete deployment neo4j-db graphql math-api pandas-api visualisation-api

kubectl delete ing minikube-ingress