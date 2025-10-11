cat >scripts/setup.sh <<'EOF'
#!/bin/bash
set -euo pipefail

echo ">>> Atualizando e instalando dependências básicas"
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git build-essential ca-certificates

echo ">>> Instalando Docker (repo oficial) e compose plugin"
sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  \$(. /etc/os-release && echo \$UBUNTU_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo ">>> Habilitando Docker"
sudo systemctl enable --now docker
sudo usermod -aG docker \$USER

echo ">>> Instalando Rust (noninteractive)"
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source \$HOME/.cargo/env

echo ">>> Instalando Python & pip"
sudo apt install -y python3 python3-pip python3-venv

echo ">>> Instalando PostgreSQL"
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
sudo -u postgres psql -c "CREATE USER etl_user WITH PASSWORD 'supersecret';" || true
sudo -u postgres psql -c "CREATE DATABASE weather_db OWNER etl_user;" || true

echo ">>> Copy .env.example to .env (edit .env to add API keys and tokens)"
cp .env.example .env || true

echo ">>> Setup done. Please logout/login to apply docker group change. Edit .env then run: docker compose up --build -d"
EOF

chmod +x scripts/setup.sh
