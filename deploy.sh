
zip lambda lambda.py
terraform apply -auto-approve

# test
aws lambda invoke --cli-binary-format raw-in-base64-out --log-type Tail --function-name minimal_lambda_function --payload '{ "name": "Bob" }' response.json | jq .LogResult | sed 's/"//g' | base64 --decode

# cleanup
rm lambda.zip

