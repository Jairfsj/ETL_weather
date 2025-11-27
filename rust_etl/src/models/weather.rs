use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WeatherData {
    pub city: String,
    pub temperature: f64,
    pub feels_like: f64,
    pub humidity: i32,
    pub pressure: i32,
    pub wind_speed: f64,
    pub wind_direction: Option<f64>,
    pub weather_main: String,
    pub weather_description: String,
    pub weather_icon: String,
    pub timestamp: i64,
    pub timezone: i32,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

impl WeatherData {
    pub fn from_api_response(response: &ApiResponse) -> Self {
        let weather = response.weather.first();
        let weather_main = weather.map(|w| w.main.clone()).unwrap_or_else(|| "Unknown".to_string());
        let weather_description = weather.map(|w| w.description.clone()).unwrap_or_else(|| "Unknown".to_string());
        let weather_icon = weather.map(|w| w.icon.clone()).unwrap_or_else(|| "01d".to_string());

        Self {
            city: response.name.clone(),
            temperature: response.main.temp,
            feels_like: response.main.feels_like,
            humidity: response.main.humidity,
            pressure: response.main.pressure,
            wind_speed: response.wind.speed,
            wind_direction: response.wind.deg,
            weather_main,
            weather_description,
            weather_icon,
            timestamp: response.dt,
            timezone: response.timezone,
            created_at: chrono::Utc::now(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct WeatherMain {
    pub temp: f64,
    pub feels_like: f64,
    pub humidity: i32,
    pub pressure: i32,
}

#[derive(Debug, Deserialize)]
pub struct Wind {
    pub speed: f64,
    #[serde(default)]
    pub deg: Option<f64>,
}

#[derive(Debug, Deserialize)]
pub struct Weather {
    pub id: i32,
    pub main: String,
    pub description: String,
    pub icon: String,
}

#[derive(Debug, Deserialize)]
pub struct ApiResponse {
    pub coord: Coordinates,
    pub weather: Vec<Weather>,
    pub base: String,
    pub main: WeatherMain,
    pub visibility: Option<i32>,
    pub wind: Wind,
    pub clouds: Clouds,
    pub dt: i64,
    pub sys: Sys,
    pub timezone: i32,
    pub id: i64,
    pub name: String,
    pub cod: i32,
}

#[derive(Debug, Deserialize)]
pub struct Coordinates {
    pub lon: f64,
    pub lat: f64,
}

#[derive(Debug, Deserialize)]
pub struct Clouds {
    pub all: i32,
}

#[derive(Debug, Deserialize)]
pub struct Sys {
    #[serde(rename = "type")]
    pub sys_type: Option<i32>,
    pub id: Option<i64>,
    pub country: Option<String>,
    pub sunrise: Option<i64>,
    pub sunset: Option<i64>,
}

