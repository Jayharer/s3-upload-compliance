
resource "aws_s3_bucket" "s3_source_bucket" {
    bucket = "aws-devops-project02-source-bucket"
    force_destroy = true
    tags = {
      Environment = "dev"
    }
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_s3_upload_arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.s3_source_bucket.arn
}

resource "aws_s3_bucket_notification" "s3_src_bucket_notification" {
  bucket = aws_s3_bucket.s3_source_bucket.id

  lambda_function {
    lambda_function_arn = var.lambda_s3_upload_arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_bucket]
}