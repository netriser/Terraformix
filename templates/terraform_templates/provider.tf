terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>4"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = "{{ region }}"

}

data "aws_availability_zones" "available" {}


