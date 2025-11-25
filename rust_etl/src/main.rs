use anyhow::Result;
use dotenvy::dotenv;
use log::{info, warn, error};
use reqwest::Client;
use serde::Deserialize;
use sqlx::PgPool;
use std::env;
use tokio::time::{sleep, Duration};

#[derive(Deserialize)]
struct WeatherMain {
    temp: f64,
    humidity: i32,
    pressure: i32,
    feels_like: f64,
}

#[derive(Deserialize)]
struct Wind {
    speed: f64,
    deg: Option<f64>,
}

#[derive(Deserialize)]
struct Weather {
    id: i32,
    main: String,
    description: String,
    icon: String,
}

#[derive(Deserialize)]
struct ApiResponse {
    name: String,
    main: WeatherMain,
    wind: Wind,
    weather: Vec<Weather>,
    dt: i64,
    timezone: i32,
    cod: i32,
}

async fn fetch_weather(client: &Client, url: &str) -> Result<ApiResponse> {
    let resp = client.get(url).send().await?.error_for_status()?;
    Ok(resp.json().await?)
}

async fn insert_weather(pool: &PgPool, data: &ApiResponse) -> Result<()> {
    let weather = data.weather.first();

    sqlx::query(
        "INSERT INTO weather_data (city, temperature, feels_like, humidity, pressure, wind_speed, wind_direction, weather_main, weather_description, weather_icon, timestamp, timezone) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)"
    )
    .bind(&data.name)
    .bind(data.main.temp)
    .bind(data.main.feels_like)
    .bind(data.main.humidity)
    .bind(data.main.pressure)
    .bind(data.wind.speed)
    .bind(data.wind.deg)
    .bind(weather.map(|w| &w.main))
    .bind(weather.map(|w| &w.description))
    .bind(weather.map(|w| &w.icon))
    .bind(data.dt)
    .bind(data.timezone)
    .execute(pool)
    .await?;
    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenv().ok();
    env_logger::init();

    let api_key = env::var("OPENWEATHER_API_KEY").expect("OPENWEATHER_API_KEY not set");
    let city = env::var("CITY").unwrap_or_else(|_| "Montreal".to_string());

    // Compose DB URL from .env
    let db_user = env::var("POSTGRES_USER").unwrap_or_else(|_| "etl_user".into());
    let db_pass = env::var("POSTGRES_PASSWORD").unwrap_or_else(|_| "supersecret".into());
    let db_host = env::var("POSTGRES_HOST").unwrap_or_else(|_| "postgres".into());
    let db_port = env::var("POSTGRES_PORT").unwrap_or_else(|_| "5432".into());
    let db_name = env::var("POSTGRES_DB").unwrap_or_else(|_| "weather_db".into());
    let db_url = format!("postgres://{}:{}@{}:{}/{}", db_user, db_pass, db_host, db_port, db_name);

    let interval: u64 = env::var("ETL_INTERVAL")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(43200);

    let pool = PgPool::connect(&db_url).await?;
    let client = Client::new();

    let url = format!("http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric", city, api_key);

    loop {
        info!("Fetching weather from: {}", &url);
        match fetch_weather(&client, &url).await {
            Ok(data) => {
                match insert_weather(&pool, &data).await {
                    Ok(_) => {
                        let weather_desc = data.weather.first().map(|w| &w.description).unwrap_or("unknown");
                        let weather_main = data.weather.first().map(|w| &w.main).unwrap_or("unknown");
                        info!("✅ Weather data inserted: {} - 🌡️ {:.1}°C (feels like {:.1}°C), 💧 {}%, 🌬️ {:.1}km/h, ☁️ {} ({})",
                              data.name, data.main.temp, data.main.feels_like, data.main.humidity, data.wind.speed, weather_main, weather_desc);
                    },
                    Err(e) => error!("❌ Database insert failed: {:?}", e),
                }
            }
            Err(e) => warn!("Fetch failed: {:?}", e),
        }
        sleep(Duration::from_secs(interval)).await;
    }
}
