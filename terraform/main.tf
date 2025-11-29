terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "eu-west-3"
# TODO:
#   access_key                  = ""
#   secret_key                  = ""
#   s3_force_path_style         = true
  skip_credentials_validation = true
  skip_region_validation      = true
  skip_requesting_account_id  = true
}
