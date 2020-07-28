variable "region" {
  type    = string
  default = "eu-central-1"
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
