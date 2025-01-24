
variable "AWS_REGION" {
  type    = string
  default = "us-east-1"
}

variable "lambda_s3_upload_arn" {
  type    = string
  default = "arn:aws:lambda:us-east-1:861936062471:function:sam-app-s3-upload-S3UploadFunction-mIKRp4FZFj5n"
}
