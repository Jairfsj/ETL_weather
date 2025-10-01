#builder

FROM rust:1.71 as builder
WORKDIR /usr/src/rust_etl

#cache dependencies

COPY Cargo.toml Cargo.lock ./Cargo.toml
RUN mkdir src && echo "fn main () { println!(\"dummy\"); }" > src/main.rs 
RUN cargo build --release || true 

#copy actual source

COPY . .
RUN rm -f src/main.rs
RUN cargo build --release

# runtime

FROM debian:bullseye-slim
RUN apt-get update && apt-get install -y ca-certificates tzdata && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/rust_elt/target/release/rust_etl /usr/local/bin/rust_elt
WORKDIR /app 
COPY .env .env 
ENV RUST_LOG=info
CMD ["/usr/local/bin/rust_etl"]




