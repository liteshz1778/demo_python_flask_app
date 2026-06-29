#!/bin/bash

kubectl create -f msqldb-secret.yaml
kubectl create -f webapp-cm.yml
kubectl create -f sts-headless-svc-mysqldb.yaml
kubectl create -f host-pv.yaml
kubectl create -f mysql-sc.yaml
kubectl create -f deployment-svc-webapp-flask.yaml

echo;
echo -e "\n*****************************************\n"

export WEBAPP_NODEPORT=$(kubectl get svc flask-webapp-svc -o jsonpath='{.spec.ports[0].nodePort}')

echo "WEBAPP_NODEPORT=${WEBAPP_NODEPORT}"

echo -e "\n*****************************************\n"
