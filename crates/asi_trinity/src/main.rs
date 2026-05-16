use std::env;

#[tokio::main]
async fn main() {
    let mode = env::var("ASI_MODE").unwrap_or_else(|_| "alba".to_string());

    match mode.as_str() {
        "alba" => run_alba().await,
        "albi" => run_albi().await,
        "jona" => run_jona().await,
        "controller" => run_controller().await,
        _ => panic!("Unknown ASI_MODE"),
    }
}

async fn run_alba() {
    println!("ALBA running...");
}

async fn run_albi() {
    println!("ALBI running...");
}

async fn run_jona() {
    println!("JONA running...");
}

async fn run_controller() {
    println!("ASI Trinity controller running...");
}
