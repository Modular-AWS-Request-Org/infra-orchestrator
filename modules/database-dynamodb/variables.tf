variable "project_name" {
  type = string
}

variable "base_role_name" {
  type = string
}

variable "billing_mode" {
  type    = string
  default = "PAY_PER_REQUEST"
}

variable "hash_key" {
  type = string
}

variable "hash_key_type" {
  type    = string
  default = "S"
}

variable "range_key" {
  type    = string
  default = ""
}

variable "range_key_type" {
  type    = string
  default = ""
}

variable "enable_point_in_time_recovery" {
  type    = bool
  default = true
}
