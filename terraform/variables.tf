variable "region" {
  type    = string
  default = "eu-central-1"
}

variable "tags" {
  default = {
    application = "daytobase"
  }
  description = "Application tag to mark Daytobase resources"
  type        = map(string)
}
