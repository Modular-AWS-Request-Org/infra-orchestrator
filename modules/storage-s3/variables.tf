variable "project_name" {
  type = string
}

variable "base_role_name" {
  type = string
}

variable "versioning" {
  type    = bool
  default = true
}

variable "encryption" {
  type    = string
  default = "AES256"
}
