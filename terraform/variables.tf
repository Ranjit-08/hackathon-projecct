variable "aws_region" {
  default = "us-east-1"
}

variable "db_password" {
  description = "RDS Master Password"
  sensitive   = true
}

variable "db_username" {
  default = "admin"
}

variable "smtp_user" {
  description = "Gmail address"
}

variable "smtp_password" {
  description = "Gmail App Password"
  sensitive   = true
}

variable "groq_api_key" {
  description = "Groq API Key"
  sensitive   = true
}

variable "jwt_secret" {
  default = "hirewalk-jwt-secret-2025"
}

variable "key_pair_name" {
  description = "EC2 Key Pair name (already created in AWS)"
}