terraform {
  backend "s3" {
    bucket = "jayambar-terraform-backend"
    key = "project02/terraform.tfstate"
    region = "us-east-1"
    profile = "default"
  }
}