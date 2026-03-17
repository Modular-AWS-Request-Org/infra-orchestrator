data "aws_iam_policy_document" "access" {
  statement {
    sid    = "StorageBucketAccess"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.this.arn,
      "${aws_s3_bucket.this.arn}/*",
    ]
  }
}

resource "aws_iam_policy" "access" {
  name   = "${var.project_name}-storage-access"
  policy = data.aws_iam_policy_document.access.json
}

resource "aws_iam_role_policy_attachment" "access" {
  role       = var.base_role_name
  policy_arn = aws_iam_policy.access.arn
}
