# 🌤️ Tableau de Bord ETL Météo Montréal

> Système ETL professionnel complet pour la collecte, le traitement et la visualisation des données météorologiques de Montréal utilisant des technologies modernes comme Rust et Python.

📖 **Lire dans d'autres langues** : [🇧🇷 Português](README.md) | [🇺🇸 English](README.en.md)

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white)](https://rust-lang.org)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

## ✨ Fonctionnalités

### 🔄 ETL en Temps Réel
- **Collecte automatique** des données de l'API OpenWeatherMap toutes les 5 minutes
- **Traitement robuste** avec gestion d'erreurs et récupération automatique
- **Stockage fiable** dans PostgreSQL avec index optimisés

### 📊 Tableau de Bord Interactif
- **Interface moderne et responsive** pour desktop et mobile
- **Visualisations en temps réel** avec graphiques interactifs
- **Métriques détaillées** de température, humidité, pression et vent
- **Design intuitif** pour les utilisateurs non-techniques

### 🏗️ Architecture Professionnelle
- **Microservices découplés** avec responsabilités claires
- **APIs RESTful** bien documentées
- **Conteneurisation complète** avec Docker
- **Monitoring et health checks** intégrés

## 🚀 Démarrage Rapide

### Prérequis

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Compte gratuit** sur [OpenWeatherMap](https://openweathermap.org/)

### 1. Clonage et Configuration

```bash
# Cloner le dépôt
git clone <repository-url>
cd montreal-weather-etl

# Copier les variables d'environnement
cp .env.example .env
```

### 2. Configuration de l'API

1. Accéder à [https://openweathermap.org/api](https://openweathermap.org/api)
2. Créer un compte gratuit
3. Aller dans votre tableau de bord → Clés API
4. Copier votre clé d'API
5. Modifier le fichier `.env` :

```bash
# Remplacer 'your_api_key_here' par votre vraie clé
OPENWEATHER_API_KEY=your_actual_api_key_here
```

### 3. Exécution

```bash
# Construire et démarrer tous les services
docker compose up --build -d

# Vérifier le statut des conteneurs
docker compose ps

# Voir les logs en temps réel
docker compose logs -f
```

### 4. Accès

- **🌐 Tableau de Bord Web** : http://localhost:5000/dashboard
- **📡 API REST** : http://localhost:5000/api/v1/weather/health
- **🐘 PostgreSQL** : localhost:5432 (dans les conteneurs)

## 📋 Référence API

### Points de Terminaison Principaux

| Méthode | Point de terminaison | Description |
|---------|---------------------|-------------|
| `GET` | `/api/v1/weather/health` | Vérification de santé du système |
| `GET` | `/api/v1/weather/current` | Conditions météorologiques actuelles |
| `GET` | `/api/v1/weather/latest?limit=N` | Derniers N enregistrements |
| `GET` | `/api/v1/weather/stats` | Statistiques météorologiques |
| `GET` | `/api/v1/weather/chart-data?hours=N` | Données pour graphiques |

### Exemple de Réponse - Conditions Actuelles

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

## 🏛️ Architecture du Système

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenWeather   │ => │   Service ETL   │ => │  Base de        │
│   API (REST)    │    │   Rust          │    │  Données        │
└─────────────────┘    └─────────────────┘    │  PostgreSQL     │
                                              └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Python Flask   │ <= │   Tableau de    │
                       │   API REST      │    │   Bord Web      │
                       └─────────────────┘    │   (HTML/CSS/JS) │
                                              └─────────────────┘
```

### Composants

#### 1. **Service ETL Rust** (`rust_etl/`)
- **Responsabilités** : Collecte, traitement et stockage des données
- **Technologies** : Rust, Tokio, Reqwest, SQLx
- **Caractéristiques** : Haute performance, faible consommation mémoire

#### 2. **API Analytics Python** (`python_analytics/`)
- **Responsabilités** : API REST, tableau de bord web, analytics
- **Technologies** : Python, Flask, Pandas, Plotly
- **Caractéristiques** : Interface web moderne, APIs RESTful

#### 3. **Base de Données PostgreSQL**
- **Responsabilités** : Stockage persistant des données
- **Caractéristiques** : Index optimisés, contraintes d'intégrité

## ⚙️ Configuration Avancée

### Variables d'Environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `OPENWEATHER_API_KEY` | - | **Obligatoire** - Clé API OpenWeatherMap |
| `CITY` | Montreal | Ville pour la collecte de données |
| `ETL_INTERVAL` | 300 | Intervalle de collecte en secondes |
| `POSTGRES_USER` | etl_user | Utilisateur de la base de données |
| `POSTGRES_PASSWORD` | supersecret | Mot de passe de la base de données |
| `POSTGRES_DB` | weather_db | Nom de la base de données |
| `FLASK_PORT` | 5000 | Port du serveur Flask |

### Modes d'Exécution

#### Développement
```bash
# Environnement de développement complet
docker compose up --build

# Services spécifiques uniquement
docker compose up postgres python_analytics
```

#### Production
```bash
# Utiliser la configuration de production
docker compose -f docker-compose.prod.yml up --build -d
```

## 🛠️ Développement

### Structure du Projet

```
montreal-weather-etl/
├── docker-compose.yml          # Configuration de développement
├── docker-compose.prod.yml     # Configuration de production
├── .env.example               # Exemple de variables d'environnement
├── postgres/
│   └── init.sql              # Schéma initial de la base
├── rust_etl/
│   ├── Cargo.toml            # Dépendances Rust
│   ├── Dockerfile            # Conteneur Rust
│   └── src/
│       ├── lib.rs           # Bibliothèque partagée
│       ├── main.rs          # Point d'entrée
│       ├── models/          # Modèles de données
│       ├── services/        # Logique métier
│       ├── config/          # Configuration
│       └── utils/           # Utilitaires
└── python_analytics/
    ├── requirements.txt      # Dépendances Python
    ├── Dockerfile           # Conteneur Python
    └── app/
        ├── __init__.py      # Application Flask
        ├── models/          # Modèles Python
        ├── services/        # Services Python
        ├── api/             # Points de terminaison REST
        ├── utils/           # Utilitaires
        └── templates/       # Templates HTML
```

### Commandes Utiles

```bash
# Nettoyer conteneurs et volumes
docker compose down -v

# Reconstruire service spécifique
docker compose build rust_etl

# Exécuter tests (quand implémentés)
docker compose exec rust_etl cargo test

# Voir statistiques des conteneurs
docker stats

# Sauvegarde de la base de données
docker compose exec postgres pg_dump -U etl_user weather_db > backup.sql
```

## 📊 Monitoring

### Health Checks
- **PostgreSQL** : Vérification de connectivité
- **API Python** : Point de terminaison `/api/v1/weather/health`
- **ETL Rust** : Monitoring automatique des processus

### Logs
```bash
# Tous les logs
docker compose logs -f

# Logs d'un service spécifique
docker compose logs -f python_analytics

# Logs avec timestamps
docker compose logs --timestamps
```

### Métriques
- Nombre total d'enregistrements collectés
- Taux de succès des collectes
- Temps de réponse de l'API
- Statut des services

## 🔒 Sécurité

- ✅ **Clés API** stockées dans les variables d'environnement
- ✅ **Conteneurs non-privilégiés** (`no-new-privileges`)
- ✅ **Système de fichiers en lecture seule** où possible
- ✅ **Réseaux isolés** entre conteneurs
- ✅ **Health checks** automatisés
- ✅ **Logs structurés** avec rotation

## 🧪 Tests

```bash
# Tests Rust
cd rust_etl && cargo test

# Tests Python (quand implémentés)
cd python_analytics && python -m pytest

# Tests d'intégration
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚀 Déploiement

### Production

1. **Configurer les variables d'environnement** :
   ```bash
   cp .env.example .env
   # Modifier .env avec les valeurs de production
   ```

2. **Exécuter en mode production** :
   ```bash
   docker compose -f docker-compose.prod.yml up --build -d
   ```

3. **Configurer proxy inverse** (nginx recommandé) :
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

### Évolutivité

- **Service ETL** : Stateless, peut être mis à l'échelle horizontalement
- **Service API** : Stateless, peut utiliser load balancer
- **Base de données** : Utiliser des répliques de lecture si nécessaire

## 🤝 Contribution

1. **Fork** le projet
2. **Clone** votre fork : `git clone https://github.com/your-username/montreal-weather-etl`
3. **Créer** une branche : `git checkout -b feature/AmazingFeature`
4. **Commit** vos changements : `git commit -m 'Add some AmazingFeature'`
5. **Push** vers la branche : `git push origin feature/AmazingFeature`
6. **Ouvrir** une Pull Request

### Directives de Contribution

- Suivre les standards de code (Rust : `cargo fmt`, Python : `black`)
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation
- Utiliser des commits descriptifs

## 📝 Licence

Ce projet est sous licence **MIT License** - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [OpenWeatherMap](https://openweathermap.org/) - API de données météorologiques
- [Rust Language](https://rust-lang.org/) - Langage de programmation
- [Python](https://python.org/) - Écosystème de développement
- [PostgreSQL](https://postgresql.org/) - Base de données robuste
- [Docker](https://docker.com/) - Conteneurisation

## 📞 Support

Pour le support technique ou les questions :

1. Vérifier les [logs des conteneurs](#logs)
2. Consulter la [documentation API](#api-reference)
3. Ouvrir une [issue](https://github.com/your-username/montreal-weather-etl/issues) sur GitHub

---

**⭐ Si ce projet vous a été utile, considérez de lui donner une étoile sur GitHub !**
