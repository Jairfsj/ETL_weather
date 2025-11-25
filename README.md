# 🌤️ Montreal Weather ETL Dashboard

Sistema ETL completo para coleta, processamento e visualização de dados climáticos de Montreal usando Rust e Python.

## 🚀 Funcionalidades

- **ETL em Rust**: Coleta automática de dados da API OpenWeatherMap
- **Dashboard em Python/Flask**: Visualização interativa dos dados
- **PostgreSQL**: Armazenamento robusto dos dados
- **Docker**: Containerização completa para fácil deployment

## 📋 Pré-requisitos

- Docker e Docker Compose
- Conta gratuita no [OpenWeatherMap](https://openweathermap.org/)

## 🔧 Configuração

### 1. Obter Chave da API

1. Acesse [https://openweathermap.org/](https://openweathermap.org/)
2. Crie uma conta gratuita
3. Vá para seu dashboard e copie sua API Key

### 2. Configurar Ambiente

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env e adicione sua chave da API
nano .env
```

### 3. Executar o Sistema

```bash
# Construir e executar todos os serviços
docker compose up --build -d

# Ver logs (opcional)
docker compose logs -f
```

### 4. Acessar o Dashboard

- **Dashboard Web**: http://localhost:5000/dashboard
- **API JSON**: http://localhost:5000/latest

## 🏗️ Arquitetura

### Serviços

- **PostgreSQL**: Banco de dados para armazenar dados climáticos
- **rust_etl**: Serviço ETL que coleta dados da API a cada 5 minutos
- **python_analytics**: API Flask com dashboard interativo

### Estrutura dos Dados

A tabela `weather_data` armazena:

- `city`: Nome da cidade
- `temperature`: Temperatura atual (°C)
- `feels_like`: Sensação térmica (°C)
- `humidity`: Umidade relativa (%)
- `pressure`: Pressão atmosférica (hPa)
- `wind_speed`: Velocidade do vento (km/h)
- `wind_direction`: Direção do vento (°)
- `weather_main`: Condição principal (ex: "Clear", "Clouds")
- `weather_description`: Descrição detalhada
- `weather_icon`: Código do ícone
- `timestamp`: Timestamp Unix da medição
- `timezone`: Fuso horário
- `created_at`: Quando foi inserido no banco

## 🔍 API Endpoints

### GET /latest
Retorna os últimos 100 registros climáticos em JSON.

**Exemplo de resposta:**
```json
[
  {
    "city": "Montréal",
    "temperature": 15.2,
    "feels_like": 14.8,
    "humidity": 65,
    "pressure": 1013,
    "wind_speed": 3.5,
    "weather_main": "Clouds",
    "weather_description": "few clouds",
    "ts": "2025-01-25T10:30:00",
    "created_at": "2025-01-25T10:35:00"
  }
]
```

### GET /dashboard
Dashboard web interativo com gráficos e estatísticas atuais.

## 🛠️ Desenvolvimento

### Executar apenas o banco de dados
```bash
docker compose up postgres -d
```

### Executar apenas o ETL
```bash
docker compose up rust_etl -d
```

### Executar apenas o dashboard
```bash
docker compose up python_analytics -d
```

### Logs em tempo real
```bash
# Todos os serviços
docker compose logs -f

# Serviço específico
docker compose logs -f rust_etl
```

## 📊 Dashboard

O dashboard mostra:
- **Condições atuais**: Temperatura, umidade, vento, pressão
- **Gráfico de temperatura**: Evolução temporal da temperatura
- **Gráfico de umidade**: Tendências de umidade ao longo do tempo
- **Informações detalhadas**: Descrição do tempo e ícones

## 🔒 Segurança

- A chave da API é armazenada em variável de ambiente
- Comunicação interna entre containers via Docker network
- Dados climáticos são públicos (não sensíveis)

## 📝 Notas

- O ETL coleta dados a cada 5 minutos por padrão (configurável via `ETL_INTERVAL`)
- Dados históricos ficam disponíveis no dashboard
- O sistema é stateless e pode ser escalado horizontalmente

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
