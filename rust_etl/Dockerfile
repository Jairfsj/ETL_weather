#builder

FROM rust:latest as builder
WORKDIR /usr/src/rust_etl
# Build the application
COPY . .
ENV DATABASE_URL=postgres://etl_user:supersecret@postgres:5432/weather_db
RUN cargo build --release

# runtime

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/rust_etl/target/release/rust_etl /usr/local/bin/rust_etl
WORKDIR /app
ENV RUST_LOG=info
CMD ["/usr/local/bin/rust_etl"]




