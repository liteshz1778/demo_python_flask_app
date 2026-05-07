#!/bin/bash

read -p "Enter the manifest directory name: " directory_name
kubectl delete -f ./$directory_name --recursive
