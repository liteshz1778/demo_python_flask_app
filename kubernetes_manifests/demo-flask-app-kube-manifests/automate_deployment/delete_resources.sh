#!/bin/bash


kubectl delete -f sts-headless-svc-mysqldb.yaml
kubectl delete pvc --all
kubectl delete pv --all
kubectl delete -f mysql-sc.yaml
kubectl delete -f deployment-svc-webapp-flask.yaml
kubectl delete -f msqldb-secret.yaml
kubectl delete -f webapp-cm.yml

