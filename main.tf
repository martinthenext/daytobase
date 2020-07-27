provider "aws" {
  version = "~>2.70"
  region  = var.region
}

variable "function_name" {
  default = "minimal_lambda_function"
}

variable "handler" {
  default = "lambda.handler"
}

variable "runtime" {
  default = "python3.8"
}

resource "aws_lambda_function" "daytobase" {
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = var.handler
  runtime          = var.runtime
  filename         = "lambda.zip"
  function_name    = var.function_name
  source_code_hash = filesha256("lambda.zip")
}

resource "aws_iam_role" "lambda_exec_role" {
  name        = "lambda_exec"
  path        = "/"
  description = "Allows Lambda Function to call AWS services on your behalf."

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

# -----------------------------------------------------------------------------
# fucking API GATEWAY
# -----------------------------------------------------------------------------

resource "aws_api_gateway_rest_api" "lambda_api" {
  name = "lambda_api"
}

resource "aws_api_gateway_resource" "resource" {
  path_part   = "api"
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.resource.id
  http_method             = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.daytobase.arn}/invocations"
}

resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [aws_api_gateway_integration.integration]

  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  stage_name  = "prod"
}

output "api_url" {
  value = "${aws_api_gateway_deployment.deployment.invoke_url}${aws_api_gateway_resource.resource.path}"
}
