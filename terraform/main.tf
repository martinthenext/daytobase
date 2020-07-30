provider "aws" {
  version = "~>2.70"
  region  = var.region
}

provider "archive" {
  version = "~>1.3"
}

resource "null_resource" "pip" {
  triggers = {
    main         = "${base64sha256(file("../lambda/main.py"))}"
    requirements = "${base64sha256(file("../lambda/requirements.txt"))}"
  }

  provisioner "local-exec" {
    command = "rm -rf /tmp/lambda && cp -R ../lambda /tmp/lambda && pip install -r ../lambda/requirements.txt --target /tmp/lambda"
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "/tmp/lambda/"
  output_path = "/tmp/lambda.zip"

  depends_on = [null_resource.pip]
}

resource "aws_lambda_function" "daytobase" {
  tags             = var.tags
  function_name    = "daytobase_lambda"
  handler          = "main.handler"
  runtime          = "python3.8"
  role             = aws_iam_role.lambda_exec.arn
  filename         = "/tmp/lambda.zip"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      TELEGRAM_TOKEN = var.telegram_token
    }
  }
}

resource "aws_iam_role" "lambda_exec" {
  tags        = var.tags
  name        = "daytobase_iam"
  path        = "/"
  description = "Allows Lambda Function to call AWS services on your behalf."

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "logs_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.daytobase.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*/*"
}

# CloudWatch
# resource "aws_cloudwatch_log_group" "lambda_log_group" {
#   tags              = var.tags
#   name              = "/aws/lambda/${aws_lambda_function.daytobase.function_name}"
#   retention_in_days = 30
# }


# -----------------------------------------------------------------------------
# fucking API GATEWAY
# -----------------------------------------------------------------------------

resource "aws_api_gateway_rest_api" "lambda_api" {
  tags        = var.tags
  name        = "daytobase_api"
  description = "Daytobase serverless server that serves requests."
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "api"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.daytobase.invoke_arn
}

# ----- API root bullshit

# resource "aws_api_gateway_method" "proxy_root" {
#   rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
#   resource_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
#   http_method   = "ANY"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_integration" "lambda_root" {
#   rest_api_id = aws_api_gateway_rest_api.lambda_api.id
#   resource_id = aws_api_gateway_method.proxy_root.resource_id
#   http_method = aws_api_gateway_method.proxy_root.http_method

#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = aws_lambda_function.daytobase.invoke_arn
# }

#  ----

resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    # aws_api_gateway_integration.lambda_root,
  ]
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  stage_name  = "prod"

  triggers = {
    redeployment = sha1(join(",", list(
      jsonencode(aws_api_gateway_integration.lambda),
    )))
  }

  lifecycle {
    create_before_destroy = true
  }
}

output "api_url" {
  value = "${aws_api_gateway_deployment.deployment.invoke_url}/${aws_api_gateway_resource.proxy.path_part}"
}
