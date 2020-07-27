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

resource "aws_lambda_function" "lambda_function" {
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
