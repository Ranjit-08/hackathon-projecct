#!/bin/bash
set -e
exec > /var/log/user_data.log 2>&1

# ── System Setup ──────────────────────────────────────────────────────────────
yum update -y
yum install -y python3 python3-pip nginx git mariadb105-server

# ── Clone Repo ────────────────────────────────────────────────────────────────
cd /home/ec2-user
git clone https://github.com/Ranjit-08/hackathon-projecct.git
chown -R ec2-user:ec2-user hackathon-projecct

# ── Python Deps ───────────────────────────────────────────────────────────────
cd /home/ec2-user/hackathon-projecct/backend
pip3 install -r requirements.txt

# ── .env File ─────────────────────────────────────────────────────────────────
cat > /home/ec2-user/hackathon-projecct/backend/.env << EOF
DB_HOST=${db_host}
DB_PORT=3306
DB_NAME=${db_name}
DB_USER=${db_user}
DB_PASSWORD=${db_password}

JWT_SECRET=${jwt_secret}

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=${smtp_user}
SMTP_PASSWORD=${smtp_password}

GROQ_API_KEY=${groq_api_key}
GROQ_MODEL=llama-3.3-70b-versatile

DEBUG=False
PORT=5000
FRONTEND_URL=*
EOF

chown ec2-user:ec2-user /home/ec2-user/hackathon-projecct/backend/.env

# ── Wait for RDS to be ready ──────────────────────────────────────────────────
echo "Waiting for RDS..."
sleep 60

# ── Init Database ─────────────────────────────────────────────────────────────
mysql -h ${db_host} -u ${db_user} -p${db_password} < \
  /home/ec2-user/hackathon-projecct/database/schema.sql

# ── Gunicorn Path ─────────────────────────────────────────────────────────────
GUNICORN_PATH=$(which gunicorn || echo "/usr/local/bin/gunicorn")

# ── Systemd Service ───────────────────────────────────────────────────────────
cat > /etc/systemd/system/walkin.service << EOF
[Unit]
Description=HireWalk API
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/hackathon-projecct/backend
ExecStart=$GUNICORN_PATH --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# ── Frontend API URL ──────────────────────────────────────────────────────────
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
sed -i "s|http://YOUR_EC2_PUBLIC_IP/api|http://$EC2_IP/api|g" \
  /home/ec2-user/hackathon-projecct/frontend/js/api.js
sed -i "s|http://YOUR-EC2-PUBLIC-IP:5000/api|http://$EC2_IP/api|g" \
  /home/ec2-user/hackathon-projecct/frontend/js/api.js

# ── Deploy Frontend ───────────────────────────────────────────────────────────
mkdir -p /var/www/walkin-frontend
cp -r /home/ec2-user/hackathon-projecct/frontend/* /var/www/walkin-frontend/
chown -R nginx:nginx /var/www/walkin-frontend

# ── Nginx Config ──────────────────────────────────────────────────────────────
cat > /etc/nginx/conf.d/walkin.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60s;
    }

    location / {
        root /var/www/walkin-frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
EOF

# Remove default nginx server block
sed -i '/^    server {/,/^    }/d' /etc/nginx/nginx.conf

# ── Start Services ────────────────────────────────────────────────────────────
systemctl daemon-reload
systemctl enable walkin
systemctl start walkin

systemctl enable nginx
systemctl start nginx
systemctl reload nginx

echo "Deployment complete!"