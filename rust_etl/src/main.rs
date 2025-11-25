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
    humidity: i32
}

#[derive(Deserialize)]
struct Wind {
    speed: f64
}

#[derive(Deserialize)]
struct ApiResponse {
    name: String,
    main: WeatherMain,
    wind: Wind,
    dt: i64
}

async fn fetch_weather(client: &Client, url: &str) -> Result<ApiResponse> {
    let resp = client.get(url).send().await?.error_for_status()?;
    Ok(resp.json().await?)
}

async fn insert_weather(pool: &PgPool, data: &ApiResponse) -> Result<()> {
    sqlx::query(
        "INSERT INTO weather_data (city, temperature, humidity, wind_speed, timestamp) VALUES ($1, $2, $3, $4, $5)"
    )
    .bind(&data.name)
    .bind(data.main.temp)
    .bind(data.main.humidity)
    .bind(data.wind.speed)
    .bind(data.dt)
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
                    Ok(_) => info!("Inserted record: {} temp={}, humidity={}", data.name, data.main.temp, data.main.humidity),
                    Err(e) => error!("DB insert failed: {:?}", e),
                }
            }
            Err(e) => warn!("Fetch failed: {:?}", e),
        }
        sleep(Duration::from_secs(interval)).await;
    }
}