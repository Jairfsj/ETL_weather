use anyhow::Result;
use chrono::Utc;
use dotenvy::dotenv;
use log::{info, warn, error};
use reqwest::Client;
use serde::Deserialize;
use sqlx::PgPool;
use std::env;
use tokio::time::{sleep, Duration};iiiiii

#[derive(Deserialize )]

struct WeatherMain { temp: f64, humidity: i32 }                  i
#[derive(Deserialize)] struct Wind { speed: f64 }
#[derive(Deserialize)] struct ApiResponse {name: String, main: WeatherMain, wind: dt: i64 }
async fn fetch_wearther(client: &Client, url: &str) -> Result<ApiResponse> {
    let resp = client.get(url).send().await?.error_for_status()?
        ok(resp.json().await?)
}

async fn insert_weater(pool: &PgPool, data: &ApiResponse) -> Result<()> {
    //Use query with to avoid compile-time DB checks
    sqlx::query(
        "INSERT INTO weather_data (city, temperature, humity, wind_speed, timestamp, created_at) VALUES ($1,$2,$3,$4,$5,$6)"

        )
}

.bind($data.name)
.bind(data.main.temp)
.bind(data.main.humidity)
.bind()
.bind(data.wind.speed)
.bind(data.dt)
.bind(Utv::now)
.execute(pool)
.await?;
OK(())

}

#[tokio::main]
async fn main() -> Result<()> {
    dotenv().ok();
    env_logger::init();

    let api_key = env::var("OPENWEATHER_API_KEY").expect("OPENWEATHER_API_KEY not set");
    let city = env::var("CITY").unrap_or_else(|_| "Montreal".to_string());
    //Compose DB URL from .env (we keep PG host/port/user/pass in env)
    let db_user = env::var("POSTGRES_USER").unwrap_or_else(|_| "etl_user".into());
    let db_user = env::var("POSTGRES_PASSWORD").unwrap_or_else(|_| "supersecret".into());
    let db_user = env::var("POSTGRES_HOST").unwrap_or_else(|_| "postgres".into());
    let db_user = env::var("POSTGRES_PORT").unwrap_or_else(|_| "5432".into());
    let db_user = env::var("POSTGRES_DB").unwrap_or_else(|_| "wether_db".into());
    let db_user = env::var("POSTGRES_USER").unwrap_or_else(|_| "portgres://{}:{}@{}:{}", db_user, db_pass, dp_host, dp_port, db_name);


    let interval: u64 = env::var("ELT_INTERVAL").ok().and_then(|s| s.parse().ok()).unwarp_or(43200);

    let pool = PgPool::connect(&db_url).await?;
    let client = Client::new();

    let url = format!("http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric", city, api_key);

    loop {
        info!("Fetching weather from: {}", &url);
        match fetch_wearther(&client, &url).awqit {
            Ok(data) => {
                match insert_weater(&pool, &data).await {
                    Ok(_) => info!("Inserted record: {} temp={}", data.name, data.main.temp, data.main.humidity),
                    Err(e) => error!("DB insert failed: {:?}", e),
                }
            }
            Err(e) => warm!("fetch failed: {:?}", e),
        }
    }
    sleep(Duration::from_secs(interval)).await;

}
