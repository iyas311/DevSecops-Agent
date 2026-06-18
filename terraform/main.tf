provider "aws" {
  region = "us-east-1" # Change to your preferred region
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical's AWS Account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# --- IAM Role for EC2 Instance ---

resource "aws_iam_role" "agent_role" {
  name = "DevSecOpsAgentRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Attach SecurityAudit policy for read-only security checks (GuardDuty, SecurityHub, IAM, Config, etc.)
resource "aws_iam_role_policy_attachment" "security_audit_attach" {
  role       = aws_iam_role.agent_role.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}

# Attach Bedrock policy to allow the AI to function
resource "aws_iam_role_policy_attachment" "bedrock_attach" {
  role       = aws_iam_role.agent_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}

# Instance profile to attach the role to the EC2 instance
resource "aws_iam_instance_profile" "agent_profile" {
  name = "DevSecOpsAgentProfile"
  role = aws_iam_role.agent_role.name
}

# --- Security Group ---

# Create a security group allowing all traffic (as requested)
# Note: For production, you should restrict this to your IP and specific ports (22, 8000, 8501)
resource "aws_security_group" "agent_sg" {
  name        = "devsecops_agent_sg"
  description = "Allow all inbound and outbound traffic"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- EC2 Instance ---

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium"
  
  # Attach the IAM role to give the agent permissions
  iam_instance_profile = aws_iam_instance_profile.agent_profile.name

  # Associates the security group with the instance
  vpc_security_group_ids = [aws_security_group.agent_sg.id]

  # User data script to install Docker and Docker Compose automatically on boot
  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y ca-certificates curl gnupg
              
              # Add Docker's official GPG key
              install -m 0755 -d /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
              chmod a+r /etc/apt/keyrings/docker.gpg
              
              # Set up the repository
              echo \
                "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
                "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
                tee /etc/apt/sources.list.d/docker.list > /dev/null
                
              apt-get update -y
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
              
              systemctl enable docker
              systemctl start docker
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "DevSecOps-Agent-Host"
  }
}

output "instance_public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}
