#!/bin/bash

echo "Creating the volume..."

kubectl apply -f ./kompose-factory/database-volume.yaml

sleep 1s

kubectl create -f ./kompose-factory/database-deployment.yaml
kubectl create -f ./kompose-factory/database-service.yaml


echo "Creating the math api deployment and service..."

kubectl create -f ./kompose-factory/math-api-deployment.yaml
kubectl create -f ./kompose-factory/math-api-service.yaml

echo "Creating the pandas-api deployment and service..."

kubectl create -f ./kompose-factory/pandas-api-deployment.yaml
kubectl create -f ./kompose-factory/pandas-api-service.yaml

echo "Creating the visualisation-api deployment and service..."

kubectl create -f ./kompose-factory/visualisation-api-deployment.yaml
kubectl create -f ./kompose-factory/visualisation-api-service.yaml

echo "Creating the grapqhl deployment and service..."

kubectl create -f ./kompose-factory/graphql-deployment.yaml
kubectl create -f ./kompose-factory/graphql-service.yaml

echo "Adding the ingress..."

sleep 5s

sudo minikube addons enable ingress
kubectl apply -f ./kompose-factory/minikube-ingress.yaml

