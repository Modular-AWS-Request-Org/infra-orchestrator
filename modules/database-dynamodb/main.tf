resource "aws_dynamodb_table" "this" {
  name           = "${var.project_name}-table"
  billing_mode   = var.billing_mode
  hash_key       = var.hash_key
  read_capacity  = var.billing_mode == "PROVISIONED" ? 5 : null
  write_capacity = var.billing_mode == "PROVISIONED" ? 5 : null
  range_key      = var.range_key != "" ? var.range_key : null

  attribute {
    name = var.hash_key
    type = var.hash_key_type
  }

  dynamic "attribute" {
    for_each = var.range_key != "" ? [var.range_key] : []

    content {
      name = attribute.value
      type = var.range_key_type
    }
  }

  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  server_side_encryption {
    enabled = true
  }
}
