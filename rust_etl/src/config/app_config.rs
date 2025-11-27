use std::env;

#[derive(Debug, Clone)]
pub struct AppConfig {
    pub database_url: String,
    pub api_key: String,
    pub city: String,
    pub interval_seconds: u64,
    pub log_level: String,
}

impl AppConfig {
    pub fn from_env() -> Result<Self, Box<dyn std::error::Error>> {
        dotenvy::dotenv().ok();

        let database_url = format!(
            "postgres://{}:{}@{}:{}/{}",
            env::var("POSTGRES_USER").unwrap_or_else(|_| "etl_user".to_string()),
            env::var("POSTGRES_PASSWORD").unwrap_or_else(|_| "supersecret".to_string()),
            env::var("POSTGRES_HOST").unwrap_or_else(|_| "postgres".to_string()),
            env::var("POSTGRES_PORT").unwrap_or_else(|_| "5432".to_string()),
            env::var("POSTGRES_DB").unwrap_or_else(|_| "weather_db".to_string())
        );

        let api_key = env::var("OPENWEATHER_API_KEY")
            .map_err(|_| "OPENWEATHER_API_KEY environment variable is required")?;

        let city = env::var("CITY").unwrap_or_else(|_| "Montreal".to_string());

        let interval_seconds = env::var("ETL_INTERVAL")
            .unwrap_or_else(|_| "300".to_string())
            .parse()
            .unwrap_or(300);

        let log_level = env::var("RUST_LOG").unwrap_or_else(|_| "info".to_string());

        Ok(Self {
            database_url,
            api_key,
            city,
            interval_seconds,
            log_level,
        })
    }
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            database_url: "postgres://etl_user:supersecret@postgres:5432/weather_db".to_string(),
            api_key: "demo_key".to_string(),
            city: "Montreal".to_string(),
            interval_seconds: 300,
            log_level: "info".to_string(),
        }
    }
}

