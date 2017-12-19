#!/bin/bash
LLL=$1
curl -v -H "X-Broker-Api-Version: 2.3" "http://$USER:$PASS@$URI/v2/service_instances/$SII/last_operation?operation=$LLL&plan_id=$PI&service_id=$SI"
