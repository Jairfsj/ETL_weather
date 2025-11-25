pub mod logging;

pub fn setup_panic_hook() {
    std::panic::set_hook(Box::new(|panic_info| {
        eprintln!("🚨 Application panicked: {:?}", panic_info);
        std::process::exit(1);
    }));
}

pub fn graceful_shutdown() {
    log::info!("🛑 Initiating graceful shutdown...");
    std::process::exit(0);
}
