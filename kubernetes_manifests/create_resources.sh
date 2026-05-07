#!/bin/bash

read -p "Enter the manifest directory name: " directory_name
kubectl create -f ./$directory_name --recursive
