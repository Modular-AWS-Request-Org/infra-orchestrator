data "aws_iam_policy_document" "deploy" {
  statement {
    sid    = "BucketDeployAccess"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.this.arn,
      "${aws_s3_bucket.this.arn}/*",
    ]
  }

  statement {
    sid     = "CloudFrontInvalidationAccess"
    effect  = "Allow"
    actions = ["cloudfront:CreateInvalidation"]
    resources = [
      aws_cloudfront_distribution.this.arn,
    ]
  }
}

resource "aws_iam_policy" "deploy" {
  name   = "${var.project_name}-frontend-deploy"
  policy = data.aws_iam_policy_document.deploy.json
}

resource "aws_iam_role_policy_attachment" "deploy" {
  role       = var.base_role_name
  policy_arn = aws_iam_policy.deploy.arn
}
