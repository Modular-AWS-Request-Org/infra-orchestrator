output "bucket_name" {
  value = aws_s3_bucket.this.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.this.arn
}

output "distribution_id" {
  value = aws_cloudfront_distribution.this.id
}

output "distribution_url" {
  value = aws_cloudfront_distribution.this.domain_name
}

output "deploy_policy_arn" {
  value = aws_iam_policy.deploy.arn
}
