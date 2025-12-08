mod models;
mod services;
mod config;
mod utils;

use crate::{
    config::app_config::AppConfig,
    services::{database::DatabaseService, weather_service::WeatherService},
    utils::{logging, setup_panic_hook},
};
use anyhow::{Result, Context};
use log::{info, warn, error};
use std::time::Duration;
use tokio::signal::unix::{signal, SignalKind};
use tokio::time::sleep;

#[tokio::main]
async fn main() -> Result<()> {
    setup_panic_hook();

    // Initialize logging
    logging::init_logger();

    info!("🚀 Starting Montreal Weather ETL Service v1.0.0");

    // Load configuration
    let config = AppConfig::from_env()
        .context("Failed to load application configuration")?;

    info!("⚙️  Configuration loaded:");
    info!("   📍 City: {}", config.city);
    info!("   ⏱️  Collection interval: {} seconds", config.interval_seconds);
    info!("   📊 Log level: {}", config.log_level);

    // Initialize services
    let database = DatabaseService::new(&config.database_url)
        .await
        .context("Failed to initialize database connection")?;

    let weather_service = WeatherService::new(config.api_key.clone());

    // Health check
    database.health_check()
        .await
        .context("Database health check failed")?;

    info!("✅ All services initialized successfully");
    info!("🔄 Starting weather data collection loop...");

    // Setup graceful shutdown
    let mut sigterm = signal(SignalKind::terminate())
        .context("Failed to register SIGTERM handler")?;

    let mut sigint = signal(SignalKind::interrupt())
        .context("Failed to register SIGINT handler")?;

    loop {
        tokio::select! {
            // Main ETL loop
            _ = async {
                match weather_service.fetch_weather(&config.city).await {
                    Ok(weather_data) => {
                        match database.insert_weather_data(&weather_data).await {
                            Ok(_) => {
                                info!(
                                    "✅ Weather data inserted: {} - 🌡️ {:.1}°C (feels {:.1}°C), 💧 {}%, 🌬️ {:.1}km/h, ☁️ {} ({})",
                                    weather_data.city.as_deref().unwrap_or("Unknown"),
                                    weather_data.temperature,
                                    weather_data.feels_like.unwrap_or(0.0),
                                    weather_data.humidity,
                                    weather_data.wind_speed,
                                    weather_data.weather_main.as_deref().unwrap_or("Unknown"),
                                    weather_data.weather_description.as_deref().unwrap_or("Unknown")
                                );
                            }
                            Err(e) => {
                                error!("❌ Database insert failed: {}", e);
                            }
                }
            }
                    Err(e) => {
                        warn!("⚠️  Failed to fetch weather data: {}", e);
                        warn!("   Will retry in {} seconds...", config.interval_seconds);
        }
    }

                sleep(Duration::from_secs(config.interval_seconds)).await;
            } => {}

            // Handle shutdown signals
            _ = sigterm.recv() => {
                info!("🛑 Received SIGTERM signal");
                break;
            }
            _ = sigint.recv() => {
                info!("🛑 Received SIGINT signal");
                break;
            }
        }
    }

    info!("👋 Montreal Weather ETL Service stopped gracefully");
    Ok(())
}
