variable "instance_type" {
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "ami" {
  description = "Ubuntu AMI ID"
  default     = "ami-0862be96e41dcbf74" # Ubuntu 22.04 LTS in us-east-2 (Ohio)
}

variable "bucket_name" {
  description = "S3 bucket name"
  default     = "chestarz-bucket"
}

variable "ec2_name" {
  description = "Name tag for EC2 instance"
  default     = "chef_starz_server"
}

variable "db_username" {
  description = "RDS Postgres username"
  default     = "chef_starz_db"
}

variable "db_password" {
  description = "RDS Postgres password"
  sensitive   = true
  default     = "chef_starz_db_password"
}

variable "aws_profile" {
  description = "AWS CLI profile name configured locally"
  default     = "chef_starz"
}

variable "region" {
  description = "AWS region"
  default     = "us-east-2"
}