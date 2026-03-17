data "aws_iam_policy_document" "deploy" {
  statement {
    sid    = "LambdaDeployAccess"
    effect = "Allow"
    actions = [
      "lambda:GetFunction",
      "lambda:UpdateFunctionCode",
    ]
    resources = [
      aws_lambda_function.this.arn,
    ]
  }
}

resource "aws_iam_policy" "deploy" {
  name   = "${var.project_name}-lambda-deploy"
  policy = data.aws_iam_policy_document.deploy.json
}

resource "aws_iam_role_policy_attachment" "deploy" {
  role       = var.base_role_name
  policy_arn = aws_iam_policy.deploy.arn
}
