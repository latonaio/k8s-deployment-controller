#!/bin/bash

POD_ID=$(kubectl get po | awk '{print $1}' | grep -v NAME | grep -v Terminating | grep k8s-deployment-controller)
kubectl exec -it ${POD_ID} -- python3 -u main.py