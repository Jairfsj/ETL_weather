# 🔧 Guia de Solução de Problemas - ETL Weather Dashboard

## ❌ Problema: "Unable to connect" no Firefox

Se você está vendo esta mensagem ao tentar acessar `http://127.0.0.1:5000`:

```
Unable to connect
Firefox can't establish a connection to the server at 127.0.0.1:5000.
```

Siga este guia passo a passo para resolver o problema.

---

## 🧪 **Passo 1: Verificar se o Sistema Está Rodando**

### Verificar containers Docker:
```bash
# Verificar se os containers estão rodando
docker ps

# Você deve ver algo como:
CONTAINER ID   IMAGE                          COMMAND                  CREATED          STATUS                    PORTS
0547cfc1f980   etl_weather-python_analytics   "gunicorn --bind 0.0…"   2 minutes ago    Up 2 minutes (healthy)    0.0.0.0:5000->5000/tcp
7753c53b7149   etl_weather-rust_etl           "/usr/local/bin/rust…"   2 minutes ago    Up 2 minutes
fa8f9dd7a474   postgres:15-alpine             "docker-entrypoint.s…"   2 minutes ago    Up 2 minutes (healthy)   0.0.0.0:5432->5432/tcp
```

### Se nenhum container estiver rodando:
```bash
# Iniciar o sistema
cd /path/to/ETL_weather
docker compose up -d

# Aguardar 30 segundos para inicialização completa
sleep 30
```

---

## 🧪 **Passo 2: Testar Conectividade**

### Teste básico da API:
```bash
# Testar se a API está respondendo
curl -s http://127.0.0.1:5000/api/v1/weather/health

# Deve retornar:
{"database":"connected","status":"healthy","timestamp":"2024-01-01T00:00:00Z"}
```

### Teste do dashboard:
```bash
# Testar se o dashboard está respondendo
curl -s -w "%{http_code}" http://127.0.0.1:5000/dashboard | tail -1

# Deve retornar: 200
```

### Usar arquivo de teste interativo:
```bash
# Abrir arquivo de teste no navegador
# O arquivo test_connection.html contém testes interativos
# Abra diretamente no navegador: file:///path/to/ETL_weather/test_connection.html
```

---

## 🧪 **Passo 3: Verificar Porta e Firewall**

### Verificar se a porta 5000 está em uso:
```bash
# Linux/Mac
netstat -tlnp | grep 5000

# Ou verificar processos usando a porta
lsof -i :5000
```

### Se a porta estiver ocupada:
```bash
# Parar outros processos na porta 5000
sudo kill -9 $(lsof -t -i:5000)

# Ou mudar a porta no docker-compose.yml
# Alterar: "5000:5000" para "5001:5000"
# Depois: docker compose up -d
```

### Verificar firewall:
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 5000

# CentOS/RHEL/Fedora
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# macOS (desabilitar temporariamente)
sudo pfctl -d
```

---

## 🧪 **Passo 4: Testar Diferentes URLs**

Tente estas variações no navegador:

1. **http://localhost:5000/dashboard**
2. **http://127.0.0.1:5000/dashboard**
3. **http://0.0.0.0:5000/dashboard**

### Se usar WSL no Windows:
- Use o IP do WSL: `http://[IP-WSL]:5000/dashboard`
- Para encontrar o IP: `ip addr show eth0 | grep inet`

---

## 🧪 **Passo 5: Limpar Cache do Navegador**

### Firefox:
1. Pressione `Ctrl+Shift+Delete` (Linux) ou `Ctrl+Shift+Backspace` (Windows/Mac)
2. Selecione "Cache" e "Cookies"
3. Clique em "Limpar agora"
4. Feche e reabra o Firefox

### Chrome/Chromium:
1. Pressione `Ctrl+Shift+Delete`
2. Selecione "Imagens e arquivos em cache" e "Cookies"
3. Clique em "Limpar dados"

---

## 🧪 **Passo 6: Verificar Logs do Container**

### Logs do Python Analytics:
```bash
docker logs weather_python_analytics

# Ou logs em tempo real
docker logs -f weather_python_analytics
```

### Logs do PostgreSQL:
```bash
docker logs weather_postgres
```

### Reiniciar containers se necessário:
```bash
docker compose restart
```

---

## 🧪 **Passo 7: Soluções Alternativas**

### Opção A: Landing Page Standalone
```bash
# Usar a landing page independente (não requer containers)
python serve_landing_page.py

# Acessar: http://localhost:8080
```

### Opção B: Executar sem Docker
```bash
# Instalar dependências
pip install -r python_analytics/requirements.txt

# Executar diretamente
cd python_analytics
export FLASK_APP=app/__init__.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

### Opção C: Usar diferentes portas
```yaml
# Modificar docker-compose.yml
services:
  python_analytics:
    ports:
      - "8080:5000"  # Muda de 5000 para 8080
```

---

## 🧪 **Passo 8: Diagnóstico Avançado**

### Verificar configuração de rede:
```bash
# Verificar interfaces de rede
ip addr show

# Testar conectividade local
ping 127.0.0.1

# Verificar DNS
nslookup localhost
```

### Testar com diferentes navegadores:
- Firefox (problema reportado)
- Chrome/Chromium
- Edge
- Safari

### Verificar versão do Docker:
```bash
docker --version
docker compose version
```

---

## 🚀 **Soluções Rápidas Mais Comuns**

### Problema: Containers não sobem
```bash
# Limpar containers antigos
docker compose down
docker system prune -f

# Reconstruir
docker compose up -d --build
```

### Problema: Porta já em uso
```bash
# Mudar porta temporariamente
docker compose down
# Editar docker-compose.yml: "8080:5000"
docker compose up -d
# Acessar: http://localhost:8080/dashboard
```

### Problema: Firewall bloqueando
```bash
# Desabilitar firewall temporariamente
sudo systemctl stop firewalld  # CentOS/RHEL
sudo ufw disable               # Ubuntu
```

---

## 📞 **Se Nada Funcionar**

### Coletar informações de diagnóstico:
```bash
# Criar relatório de diagnóstico
echo "=== Docker Status ===" > diagnostics.txt
docker ps >> diagnostics.txt

echo -e "\n=== Docker Compose Status ===" >> diagnostics.txt
docker compose ps >> diagnostics.txt

echo -e "\n=== Network Status ===" >> diagnostics.txt
netstat -tlnp | grep 5000 >> diagnostics.txt

echo -e "\n=== Container Logs ===" >> diagnostics.txt
docker logs weather_python_analytics 2>&1 | tail -20 >> diagnostics.txt

echo -e "\n=== System Info ===" >> diagnostics.txt
uname -a >> diagnostics.txt
docker --version >> diagnostics.txt
```

### Abrir issue no GitHub com o arquivo `diagnostics.txt`

---

## 🎯 **URLs de Acesso Após Solução**

- **Dashboard Principal:** `http://localhost:5000/dashboard`
- **API Health:** `http://localhost:5000/api/v1/weather/health`
- **Landing Page:** `python serve_landing_page.py` → `http://localhost:8080`
- **Teste de Conectividade:** Abrir `test_connection.html` no navegador

---

## 📋 **Checklist de Verificação**

- [ ] Containers estão rodando (`docker ps`)
- [ ] Porta 5000 está livre (`netstat -tlnp | grep 5000`)
- [ ] API responde (`curl http://127.0.0.1:5000/api/v1/weather/health`)
- [ ] Dashboard responde (`curl http://127.0.0.1:5000/dashboard`)
- [ ] Firewall permite porta 5000
- [ ] Cache do navegador limpo
- [ ] Testado em múltiplos navegadores
- [ ] Testado com `localhost` e `127.0.0.1`

---

**Se seguir estes passos e ainda tiver problemas, verifique se há algum proxy corporativo ou VPN interferindo na conexão local.**

