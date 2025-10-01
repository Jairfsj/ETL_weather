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

