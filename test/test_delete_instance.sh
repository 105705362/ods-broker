curl -v -H "X-Broker-Api-Version: 2.3" "http://$USER:$PASS@$URI/v2/service_instances/$SII?accepts_incomplete=true&plan_id=$PI&service_id=$SI" -X DELETE
