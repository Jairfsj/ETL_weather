#builder

FROM rust:latest as builder
WORKDIR /usr/src/rust_etl
# Build the application
COPY . .
    ENV DATABASE_URL=postgres://etl_user:supersecret@postgres:5432/weather_db
    ENV OPENWEATHER_API_KEY=demo_key
    ENV CITY=Montreal
    ENV ETL_INTERVAL=300
    ENV RUST_LOG=info
RUN cargo build --release

# runtime

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/rust_etl/target/release/rust_etl /usr/local/bin/rust_etl
WORKDIR /app 
ENV RUST_LOG=info
CMD ["/usr/local/bin/rust_etl"]




