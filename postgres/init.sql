CREATE TABLE IF NOT EXISTS weather_data (
  id SERIAL PRIMARY KEY,
  city VARCHAR(100),
  temperature DOUBLE PRECISION NOT NULL,
  humidity INTEGER NOT NULL,
  wind_speed DOUBLE PRECISION NOT NULL,
  timestamp BIGINT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weather_timestamp on weather_data(timestamp);
