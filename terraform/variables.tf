variable "resource_group_name" {
  type    = string
  default = "subnet-analyzer-rg"
}

variable "location" {
  type    = string
  default = "uaenorth"
}

variable "acr_name" {
  type    = string
  default = "subnetanalyzerrg1234"
}

variable "image_name" {
  type    = string
  default = "subnet-analyzer"
}

variable "sa_name" {
  type    = string
  default = "subnetanalyzersa"
}

variable "subscription_id" {
  type = string
}
variable "tenant_id" {
  type = string
}
