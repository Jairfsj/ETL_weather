use crate::models::weather::WeatherData;
use sqlx::{PgPool, postgres::PgPoolOptions};
use std::time::Duration;
use anyhow::{Result, Context};

pub struct DatabaseService {
    pool: PgPool,
}

impl DatabaseService {
    pub async fn new(database_url: &str) -> Result<Self> {
        let pool = PgPoolOptions::new()
            .max_connections(5)
            .acquire_timeout(Duration::from_secs(30))
            .connect(database_url)
            .await
            .context("Failed to connect to database")?;

        Ok(Self { pool })
    }

    pub async fn insert_weather_data(&self, data: &WeatherData) -> Result<()> {
        sqlx::query(
            r#"
            INSERT INTO weather_data (
                city, temperature, feels_like, humidity, pressure,
                wind_speed, wind_direction, weather_main, weather_description,
                weather_icon, timestamp, timezone
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            "#
        )
        .bind(&data.city)
        .bind(data.temperature)
        .bind(data.feels_like)
        .bind(data.humidity)
        .bind(data.pressure)
        .bind(data.wind_speed)
        .bind(data.wind_direction)
        .bind(&data.weather_main)
        .bind(&data.weather_description)
        .bind(&data.weather_icon)
        .bind(data.timestamp)
        .bind(data.timezone)
        .execute(&self.pool)
        .await
        .context("Failed to insert weather data")?;

        Ok(())
    }

    pub async fn get_latest_weather(&self, city: &str) -> Result<Option<WeatherData>> {
        let record = sqlx::query_as!(
            WeatherData,
            r#"
            SELECT
                city,
                temperature,
                feels_like,
                humidity,
                pressure,
                wind_speed,
                wind_direction,
                weather_main,
                weather_description,
                weather_icon,
                timestamp,
                timezone,
                created_at
            FROM weather_data
            WHERE city = $1
            ORDER BY timestamp DESC
            LIMIT 1
            "#,
            city
        )
        .fetch_optional(&self.pool)
        .await
        .context("Failed to fetch latest weather data")?;

        Ok(record)
    }

    pub async fn health_check(&self) -> Result<()> {
        sqlx::query("SELECT 1")
            .execute(&self.pool)
            .await
            .context("Database health check failed")?;
        Ok(())
    }
}
