use crate::models::weather::{ApiResponse, WeatherData};
use reqwest::Client;
use std::time::Duration;
use anyhow::{Result, Context};

pub struct WeatherService {
    client: Client,
    api_key: String,
}

impl WeatherService {
    pub fn new(api_key: String) -> Self {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .user_agent("WeatherETL/1.0")
            .build()
            .expect("Failed to create HTTP client");

        Self { client, api_key }
    }

    pub async fn fetch_weather(&self, city: &str) -> Result<WeatherData> {
        let url = format!(
            "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric",
            city, self.api_key
        );

        log::info!("🌤️  Fetching weather data for {} from OpenWeatherMap", city);

        let response = self.client
            .get(&url)
            .send()
            .await
            .context("Failed to send request to OpenWeatherMap API")?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            return Err(anyhow::anyhow!(
                "OpenWeatherMap API returned {}: {}",
                status,
                error_text
            ));
        }

        let api_response: ApiResponse = response
            .json()
            .await
            .context("Failed to parse OpenWeatherMap API response")?;

        if api_response.cod != 200 {
            return Err(anyhow::anyhow!(
                "OpenWeatherMap API returned error code: {}",
                api_response.cod
            ));
        }

        let weather_data = WeatherData::from_api_response(&api_response);

        log::info!(
            "✅ Successfully fetched weather for {}: {:.1}°C, {} ({})",
            weather_data.city,
            weather_data.temperature,
            weather_data.weather_main,
            weather_data.weather_description
        );

        Ok(weather_data)
    }
}

