output "function_name" {
  value = aws_lambda_function.this.function_name
}

output "function_arn" {
  value = aws_lambda_function.this.arn
}

output "function_url" {
  value = var.create_function_url ? aws_lambda_function_url.this[0].function_url : "none"
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.this.name
}

output "deploy_policy_arn" {
  value = aws_iam_policy.deploy.arn
}
