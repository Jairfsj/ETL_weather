# 🌤️ Montreal Weather ETL Dashboard

> Complete professional ETL system for collecting, processing and visualizing Montreal weather data using modern technologies like Rust and Python.

📖 **Read in other languages**: [🇧🇷 Português](README.md) | [🇫🇷 Français](README.fr.md)

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white)](https://rust-lang.org)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

## ✨ Features

### 🔄 Real-Time ETL
- **Automatic data collection** from OpenWeatherMap API every 5 minutes
- **Robust processing** with error handling and automatic recovery
- **Reliable storage** in PostgreSQL with optimized indexes

### 📊 Interactive Dashboard
- **Modern responsive interface** for desktop and mobile
- **Real-time visualizations** with interactive charts
- **Detailed metrics** of temperature, humidity, pressure and wind
- **Intuitive design** for non-technical users

### 🏗️ Professional Architecture
- **Decoupled microservices** with clear responsibilities
- **Well-documented RESTful APIs**
- **Complete containerization** with Docker
- **Integrated monitoring and health checks**

## 🚀 Quick Start

### Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Free account** on [OpenWeatherMap](https://openweathermap.org/)

### 1. Clone and Configuration

```bash
# Clone the repository
git clone <repository-url>
cd montreal-weather-etl

# Copy environment variables
cp .env.example .env
```

### 2. API Configuration

1. Go to [https://openweathermap.org/api](https://openweathermap.org/api)
2. Create a free account
3. Go to your dashboard → API Keys
4. Copy your API key
5. Edit the `.env` file:

```bash
# Replace 'your_api_key_here' with your actual key
OPENWEATHER_API_KEY=your_actual_api_key_here
```

### 3. Execution

```bash
# Build and start all services
docker compose up --build -d

# Check container status
docker compose ps

# View real-time logs
docker compose logs -f
```

### 4. Access

- **🌐 Web Dashboard**: http://localhost:5000/dashboard
- **📡 REST API**: http://localhost:5000/api/v1/weather/health
- **🐘 PostgreSQL**: localhost:5432 (inside containers)

## 📋 API Reference

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/weather/health` | System health check |
| `GET` | `/api/v1/weather/current` | Current weather conditions |
| `GET` | `/api/v1/weather/latest?limit=N` | Last N records |
| `GET` | `/api/v1/weather/stats` | Weather statistics |
| `GET` | `/api/v1/weather/chart-data?hours=N` | Chart data |

### Current Conditions Response Example

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

## 🏛️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenWeather   │ => │   Rust ETL      │ => │  PostgreSQL     │
│   API (REST)    │    │   Service       │    │  Database       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Python Flask   │ <= │   Web Dashboard │
                       │   REST API      │    │   (HTML/CSS/JS)  │
                       └─────────────────┘    └─────────────────┘
```

### Components

#### 1. **Rust ETL Service** (`rust_etl/`)
- **Responsibilities**: Data collection, processing and storage
- **Technologies**: Rust, Tokio, Reqwest, SQLx
- **Features**: High performance, low memory consumption

#### 2. **Python Analytics API** (`python_analytics/`)
- **Responsibilities**: REST API, web dashboard, analytics
- **Technologies**: Python, Flask, Pandas, Plotly
- **Features**: Modern web interface, RESTful APIs

#### 3. **PostgreSQL Database**
- **Responsibilities**: Persistent data storage
- **Features**: Optimized indexes, integrity constraints

## ⚙️ Advanced Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENWEATHER_API_KEY` | - | **Required** - OpenWeatherMap API key |
| `CITY` | Montreal | City for data collection |
| `ETL_INTERVAL` | 300 | Collection interval in seconds |
| `POSTGRES_USER` | etl_user | Database user |
| `POSTGRES_PASSWORD` | supersecret | Database password |
| `POSTGRES_DB` | weather_db | Database name |
| `FLASK_PORT` | 5000 | Flask server port |

### Execution Modes

#### Development
```bash
# Complete development environment
docker compose up --build

# Specific services only
docker compose up postgres python_analytics
```

#### Production
```bash
# Use production configuration
docker compose -f docker-compose.prod.yml up --build -d
```

## 🛠️ Development

### Project Structure

```
montreal-weather-etl/
├── docker-compose.yml          # Development configuration
├── docker-compose.prod.yml     # Production configuration
├── .env.example               # Environment variables example
├── postgres/
│   └── init.sql              # Initial database schema
├── rust_etl/
│   ├── Cargo.toml            # Rust dependencies
│   ├── Dockerfile            # Rust container
│   └── src/
│       ├── lib.rs           # Shared library
│       ├── main.rs          # Entry point
│       ├── models/          # Data models
│       ├── services/        # Business logic
│       ├── config/          # Configuration
│       └── utils/           # Utilities
└── python_analytics/
    ├── requirements.txt      # Python dependencies
    ├── Dockerfile           # Python container
    └── app/
        ├── __init__.py      # Flask application
        ├── models/          # Python models
        ├── services/        # Python services
        ├── api/             # REST endpoints
        ├── utils/           # Utilities
        └── templates/       # HTML templates
```

### Useful Commands

```bash
# Clean containers and volumes
docker compose down -v

# Rebuild specific service
docker compose build rust_etl

# Run tests (when implemented)
docker compose exec rust_etl cargo test

# View container statistics
docker stats

# Database backup
docker compose exec postgres pg_dump -U etl_user weather_db > backup.sql
```

## 📊 Monitoring

### Health Checks
- **PostgreSQL**: Connectivity verification
- **Python API**: `/api/v1/weather/health` endpoint
- **Rust ETL**: Automatic process monitoring

### Logs
```bash
# All logs
docker compose logs -f

# Specific service logs
docker compose logs -f python_analytics

# Logs with timestamps
docker compose logs --timestamps
```

### Metrics
- Total number of collected records
- Collection success rate
- API response time
- Service status

## 🔒 Security

- ✅ **API keys** stored in environment variables
- ✅ **Non-privileged containers** (`no-new-privileges`)
- ✅ **Read-only file system** where possible
- ✅ **Isolated networks** between containers
- ✅ **Automated health checks**
- ✅ **Structured logs** with rotation

## 🧪 Testing

```bash
# Rust tests
cd rust_etl && cargo test

# Python tests (when implemented)
cd python_analytics && python -m pytest

# Integration tests
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Deployment

### Production

1. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Run in production mode**:
   ```bash
   docker compose -f docker-compose.prod.yml up --build -d
   ```

3. **Configure reverse proxy** (nginx recommended):
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

### Scalability

- **ETL Service**: Stateless, can be scaled horizontally
- **API Service**: Stateless, can use load balancer
- **Database**: Use read replicas if needed

## 🤝 Contributing

1. **Fork** the project
2. **Clone** your fork: `git clone https://github.com/your-username/montreal-weather-etl`
3. **Create** a branch: `git checkout -b feature/AmazingFeature`
4. **Commit** your changes: `git commit -m 'Add some AmazingFeature'`
5. **Push** to the branch: `git push origin feature/AmazingFeature`
6. **Open** a Pull Request

### Contributing Guidelines

- Follow code standards (Rust: `cargo fmt`, Python: `black`)
- Add tests for new features
- Update documentation
- Use descriptive commits

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) - Weather data API
- [Rust Language](https://rust-lang.org/) - Programming language
- [Python](https://python.org/) - Development ecosystem
- [PostgreSQL](https://postgresql.org/) - Robust database
- [Docker](https://docker.com/) - Containerization

## 📞 Support

For technical support or questions:

1. Check the [container logs](#logs)
2. Consult the [API documentation](#api-reference)
3. Open an [issue](https://github.com/your-username/montreal-weather-etl/issues) on GitHub

---

**⭐ If this project was helpful to you, consider giving it a star on GitHub!**
