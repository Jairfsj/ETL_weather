use env_logger::Env;
use std::io::Write;

pub fn init_logger() {
    let env = Env::default()
        .filter_or("RUST_LOG", "info")
        .write_style_or("RUST_LOG_STYLE", "always");

    env_logger::Builder::from_env(env)
        .format(|buf, record| {
            let timestamp = buf.timestamp();
            let level = record.level();
            let target = record.target();
            let args = record.args();

            writeln!(
                buf,
                "[{}] {} {}: {}",
                timestamp,
                level,
                target,
                args
            )
        })
        .init();

    log::info!("📝 Logger initialized");
}

