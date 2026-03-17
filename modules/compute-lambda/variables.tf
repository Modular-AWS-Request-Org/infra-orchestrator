variable "project_name" {
  type = string
}

variable "base_role_arn" {
  type = string
}

variable "base_role_name" {
  type = string
}

variable "runtime" {
  type    = string
  default = "nodejs20.x"
}

variable "memory_size" {
  type    = number
  default = 256
}

variable "timeout" {
  type    = number
  default = 30
}

variable "create_function_url" {
  type    = bool
  default = false
}
