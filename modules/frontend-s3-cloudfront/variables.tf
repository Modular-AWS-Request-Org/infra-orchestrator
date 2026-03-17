variable "project_name" {
  type = string
}

variable "base_role_name" {
  type = string
}

variable "index_document" {
  type    = string
  default = "index.html"
}

variable "error_document" {
  type    = string
  default = "error.html"
}

variable "price_class" {
  type    = string
  default = "PriceClass_100"
}
