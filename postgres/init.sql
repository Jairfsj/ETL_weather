CREATE TABLE IF NOT EXISTS weather_data (
  id SERIAL PRIMARY KEY,
  city VARCHAR(100),
  temperature DOUBLE PRECISION NOT NULL,
  feels_like DOUBLE PRECISION,
  humidity INTEGER NOT NULL,
  pressure INTEGER,
  wind_speed DOUBLE PRECISION NOT NULL,
  wind_direction DOUBLE PRECISION,
  weather_main VARCHAR(50),
  weather_description VARCHAR(100),
  weather_icon VARCHAR(10),
  timestamp BIGINT NOT NULL,
  timezone INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weather_timestamp on weather_data(timestamp);
