# 🌤️ Montreal Weather ETL Dashboard

> Sistema ETL profissional completo para coleta, processamento e visualização de dados climáticos de Montreal usando tecnologias modernas como Rust e Python.

📖 **Leia em outros idiomas**: [🇺🇸 English](README.en.md) | [🇫🇷 Français](README.fr.md)

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white)](https://rust-lang.org)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

## ✨ Funcionalidades

### 🔄 ETL em Tempo Real
- **Coleta automática** de dados da API OpenWeatherMap a cada 5 minutos
- **Integração AerisWeather** para dados climáticos atuais e históricos
- **Processamento robusto** com tratamento de erros e recuperação automática
- **Armazenamento confiável** em PostgreSQL com índices otimizados

### 📊 Dashboard Interativo
- **Interface moderna** e responsiva para desktop e mobile
- **Visualizações em tempo real** com gráficos interativos
- **Métricas detalhadas** de temperatura, umidade, pressão e vento
- **Dados históricos** do AerisWeather com geração de CSVs
- **Design intuitivo** para usuários não-técnicos

### 📈 Dados Históricos AerisWeather
- **Busca por data específica** com `/api/v1/weather/aeris/historical/YYYY-MM-DD`
- **Intervalos de datas** com parâmetros `start_date` e `end_date`
- **Geração automática de CSVs** para análise histórica
- **Múltiplas localizações** em uma única consulta
- **Campos personalizáveis** para otimização de dados

### 🏗️ Arquitetura Profissional
- **Microserviços** desacoplados com responsabilidades claras
- **APIs RESTful** bem documentadas
- **Containerização completa** com Docker
- **Monitoramento e health checks** integrados

## 🚀 Início Rápido

### Pré-requisitos

- **Docker** (versão 20.10+)
- **Docker Compose** (versão 2.0+)
- **Conta gratuita** no [OpenWeatherMap](https://openweathermap.org/)
- **Conta gratuita** no [AerisWeather](https://www.aerisweather.com/) (opcional, para dados complementares)

### 1. Clonagem e Configuração

```bash
# Clone o repositório
git clone <repository-url>
cd montreal-weather-etl

# Copie as variáveis de ambiente
cp .env.example .env
```

### 2. Configuração da API

1. Acesse [https://openweathermap.org/api](https://openweathermap.org/api)
2. Crie uma conta gratuita
3. Vá para seu dashboard → API Keys
4. Copie sua chave da API
5. Edite o arquivo `.env`:

```bash
# Substitua 'your_api_key_here' pela sua chave real
OPENWEATHER_API_KEY=your_actual_api_key_here
```

### 3. Execução

```bash
# Construir e iniciar todos os serviços
docker compose up --build -d

# Verificar status dos containers
docker compose ps

# Ver logs em tempo real
docker compose logs -f
```

### 4. Acesso

- **🌐 Dashboard Web**: http://localhost:5000/dashboard
- **📡 API REST**: http://localhost:5000/api/v1/weather/health
- **🐘 PostgreSQL**: localhost:5432 (dentro dos containers)

## 📋 API Reference

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/weather/health` | Health check do sistema |
| `GET` | `/api/v1/weather/current` | Condições climáticas atuais |
| `GET` | `/api/v1/weather/latest?limit=N` | Últimos N registros |
| `GET` | `/api/v1/weather/stats` | Estatísticas do clima |
| `GET` | `/api/v1/weather/chart-data?hours=N` | Dados para gráficos |

### Exemplo de Resposta - Condições Atuais

```json
{
  "success": true,
  "data": {
    "city": "Montréal",
    "temperature": 15.2,
    "feels_like": 14.8,
    "humidity": 65,
    "pressure": 1013,
    "wind_speed": 3.5,
    "wind_direction": 250.0,
    "weather_main": "Clouds",
    "weather_description": "few clouds",
    "weather_icon": "02d",
    "timestamp": 1640995200,
    "timezone": -18000,
    "created_at": "2025-01-25T10:35:00Z"
  }
}
```

## 🏛️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenWeather   │ => │   Rust ETL      │ => │  PostgreSQL     │
│   API (REST)    │    │   Service       │    │  Database       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Python Flask   │ <= │   Web Dashboard │
                       │   REST API      │    │   (HTML/CSS/JS) │
                       └─────────────────┘    └─────────────────┘
```

### 📈 Exemplos de Uso - Dados Históricos AerisWeather

```bash
# Dados históricos de uma data específica
curl http://localhost:5000/api/v1/weather/aeris/historical/2024-01-01

# Dados históricos em intervalo de datas
curl "http://localhost:5000/api/v1/weather/aeris/historical?start_date=2024-01-01&end_date=2024-01-05"

# Gerar CSVs históricos automaticamente
curl "http://localhost:5000/api/v1/weather/aeris/historical/csv?start_date=2024-01-01&end_date=2024-01-03"

# Script Python de exemplo incluído
python historical_weather_example.py
```

### Componentes

#### 1. **Rust ETL Service** (`rust_etl/`)
- **Responsabilidades**: Coleta, processamento e armazenamento de dados
- **Tecnologias**: Rust, Tokio, Reqwest, SQLx
- **Características**: Alta performance, baixo consumo de memória

#### 2. **Python Analytics API** (`python_analytics/`)
- **Responsabilidades**: API REST, dashboard web, analytics
- **Tecnologias**: Python, Flask, Pandas, Plotly
- **Características**: Interface web moderna, APIs RESTful

#### 3. **PostgreSQL Database**
- **Responsabilidades**: Armazenamento persistente de dados
- **Características**: Índices otimizados, constraints de integridade

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `OPENWEATHER_API_KEY` | - | **Obrigatória** - Chave da API OpenWeatherMap |
| `AERIS_CLIENT_ID` | - | **Opcional** - ID do cliente AerisWeather |
| `AERIS_CLIENT_SECRET` | - | **Opcional** - Segredo do cliente AerisWeather |
| `CITY` | Montreal | Cidade para coleta de dados |
| `ETL_INTERVAL` | 300 | Intervalo de coleta em segundos |
| `POSTGRES_USER` | etl_user | Usuário do banco de dados |
| `POSTGRES_PASSWORD` | supersecret | Senha do banco de dados |
| `POSTGRES_DB` | weather_db | Nome do banco de dados |
| `FLASK_PORT` | 5000 | Porta do servidor Flask |

### Modos de Execução

#### Desenvolvimento
```bash
# Ambiente completo de desenvolvimento
docker compose up --build

# Apenas serviços específicos
docker compose up postgres python_analytics
```

#### Produção
```bash
# Usar configuração de produção
docker compose -f docker-compose.prod.yml up --build -d
```

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
montreal-weather-etl/
├── docker-compose.yml          # Configuração de desenvolvimento
├── docker-compose.prod.yml     # Configuração de produção
├── .env.example               # Exemplo de variáveis de ambiente
├── postgres/
│   └── init.sql              # Schema inicial do banco
├── rust_etl/
│   ├── Cargo.toml            # Dependências Rust
│   ├── Dockerfile            # Container Rust
│   └── src/
│       ├── lib.rs           # Biblioteca compartilhada
│       ├── main.rs          # Ponto de entrada
│       ├── models/          # Modelos de dados
│       ├── services/        # Lógica de negócio
│       ├── config/          # Configuração
│       └── utils/           # Utilitários
└── python_analytics/
    ├── requirements.txt      # Dependências Python
    ├── Dockerfile           # Container Python
    └── app/
        ├── __init__.py      # Aplicação Flask
        ├── models/          # Modelos Python
        ├── services/        # Serviços Python
        ├── api/             # Endpoints REST
        ├── utils/           # Utilitários
        └── templates/       # Templates HTML
```

### Comandos Úteis

```bash
# Limpar containers e volumes
docker compose down -v

# Reconstruir apenas um serviço
docker compose build rust_etl

# Executar testes (quando implementados)
docker compose exec rust_etl cargo test

# Ver estatísticas dos containers
docker stats

# Backup do banco de dados
docker compose exec postgres pg_dump -U etl_user weather_db > backup.sql
```

## 📊 Monitoramento

### Health Checks
- **PostgreSQL**: Verificação de conectividade
- **Python API**: Endpoint `/api/v1/weather/health`
- **Rust ETL**: Monitoramento automático de processos

### Logs
```bash
# Todos os logs
docker compose logs -f

# Logs de um serviço específico
docker compose logs -f python_analytics

# Logs com timestamps
docker compose logs --timestamps
```

### Métricas
- Número total de registros coletados
- Taxa de sucesso das coletas
- Tempo de resposta da API
- Status dos serviços

## 🔒 Segurança

- ✅ **Chaves de API** armazenadas em variáveis de ambiente
- ✅ **Containers não-privilegiados** (`no-new-privileges`)
- ✅ **File system read-only** onde possível
- ✅ **Redes isoladas** entre containers
- ✅ **Health checks** automatizados
- ✅ **Logs estruturados** com rotação

## 🧪 Testes

```bash
# Testes Rust
cd rust_etl && cargo test

# Testes Python (quando implementados)
cd python_analytics && python -m pytest

# Testes de integração
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deployment

### Produção

1. **Configure as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite .env com valores de produção
   ```

2. **Execute em modo produção**:
   ```bash
   docker compose -f docker-compose.prod.yml up --build -d
   ```

3. **Configure reverse proxy** (nginx recomendado):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Escalabilidade

- **ETL Service**: Stateless, pode ser escalado horizontalmente
- **API Service**: Stateless, pode usar load balancer
- **Database**: Use réplicas para leitura se necessário

## 🤝 Contribuição

1. **Fork** o projeto
2. **Clone** sua fork: `git clone https://github.com/your-username/montreal-weather-etl`
3. **Crie** uma branch: `git checkout -b feature/AmazingFeature`
4. **Commit** suas mudanças: `git commit -m 'Add some AmazingFeature'`
5. **Push** para a branch: `git push origin feature/AmazingFeature`
6. **Abra** um Pull Request

### Diretrizes de Contribuição

- Siga os padrões de código (Rust: `cargo fmt`, Python: `black`)
- Adicione testes para novas funcionalidades
- Atualize a documentação
- Use commits descritivos

## 📝 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [OpenWeatherMap](https://openweathermap.org/) - API de dados climáticos
- [AerisWeather](https://www.aerisweather.com/) - API de dados climáticos complementares
- [Rust Language](https://rust-lang.org/) - Linguagem de programação
- [Python](https://python.org/) - Ecossistema de desenvolvimento
- [PostgreSQL](https://postgresql.org/) - Banco de dados robusto
- [Docker](https://docker.com/) - Containerização

## 📞 Suporte

Para suporte técnico ou dúvidas:

1. Verifique os [logs dos containers](#logs)
2. Consulte a [documentação da API](#api-reference)
3. Abra uma [issue](https://github.com/your-username/montreal-weather-etl/issues) no GitHub

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!**
