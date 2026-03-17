locals {
  is_python = startswith(var.runtime, "python")
  handler   = local.is_python ? "lambda_function.handler" : "index.handler"
  src_file  = local.is_python ? "lambda_function.py" : "index.mjs"

  python_source = <<-PYTHON
  def handler(event, context):
      return {"statusCode": 200, "body": "Hello from ${var.project_name}"}
  PYTHON

  node_source = <<-NODE
  export const handler = async () => ({
    statusCode: 200,
    body: JSON.stringify({ message: "Hello from ${var.project_name}" }),
  });
  NODE

  src_code = local.is_python ? local.python_source : local.node_source
}

data "archive_file" "placeholder" {
  type                    = "zip"
  output_path             = "/tmp/${var.project_name}-lambda.zip"
  source_content          = local.src_code
  source_content_filename = local.src_file
}

resource "aws_lambda_function" "this" {
  function_name    = "${var.project_name}-function"
  role             = var.base_role_arn
  runtime          = var.runtime
  handler          = local.handler
  memory_size      = var.memory_size
  timeout          = var.timeout
  filename         = data.archive_file.placeholder.output_path
  source_code_hash = data.archive_file.placeholder.output_base64sha256
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${var.project_name}-function"
  retention_in_days = 14
}

resource "aws_lambda_function_url" "this" {
  count = var.create_function_url ? 1 : 0

  function_name      = aws_lambda_function.this.function_name
  authorization_type = "NONE"
}

resource "aws_lambda_permission" "public_url" {
  count = var.create_function_url ? 1 : 0

  statement_id           = "AllowPublicFunctionUrl"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.this.function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}
