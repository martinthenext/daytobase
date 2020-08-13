#!/bin/bash

terraform init
terraform apply -auto-approve

# test
toilet "test start" -f future --gay

aws lambda invoke --cli-binary-format raw-in-base64-out --log-type Tail \
    --function-name daytobase_lambda response.json \
    | jq .LogResult | sed 's/"//g' | base64 --decode

rm -f response.json

curl -X POST -d '{ "test": true }' "$(terraform output api_url)"

printf "\n"
toilet "test end" -f future --gay

# cleanup
# terraform destroy -auto-approve
