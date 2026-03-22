output "APP_URL" {
  value       = "http://${aws_instance.app.public_ip}"
  description = "Open this in your browser"
}

output "EC2_PUBLIC_IP" {
  value = aws_instance.app.public_ip
}

output "RDS_ENDPOINT" {
  value = aws_db_instance.mysql.address
}

output "SSH_COMMAND" {
  value = "ssh -i ${var.key_pair_name}.pem ec2-user@${aws_instance.app.public_ip}"
}