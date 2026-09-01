use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use serde_json::Value;
use std::time::{SystemTime, UNIX_EPOCH};
use std::fs;
use std::path::PathBuf;

#[derive(Serialize, Deserialize)]
struct Group {
    group_name: String,
    id: String,
    grafana_url: String,
    errors: String,
    timeouts: String,
    slow_queries: String,
    five_hundreds: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct Log {
    log: String,
    source: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct LogCount {
    source: String,
    count: usize,
}

const ONE_HOUR_IN_MILLIS: u64 = 60 * 60 * 1000;

fn get_base_dir() -> PathBuf {
    if cfg!(debug_assertions) {
        // Dev: resolve relative to the Cargo project
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
    } else {
        // Release: resolve relative to the executable
        std::env::current_exe()
            .expect("failed to get exe path")
            .parent()
            .expect("exe has no parent dir")
            .to_path_buf()
    }
}
const DS_QUERY_ENDPOINT: &str = "https://grafana.logging.sbc-tooling.com/api/ds/query?ds_type=elasticsearch&requestId=explore_63q";
const MAX_KEY_LEN: usize = 500;

#[tauri::command]
fn append_group(group: Group) -> Result<(), String> {
    let data_dir = if cfg!(debug_assertions) { get_base_dir().join("../data") } else { get_base_dir().join("data") };
    fs::create_dir_all(&data_dir).map_err(|e| e.to_string())?;

    let file_path = data_dir.join("groups.json");

    let mut groups: Vec<Group> = if file_path.exists() {
        let content = fs::read_to_string(&file_path).map_err(|e| e.to_string())?;
        serde_json::from_str(&content).map_err(|e| e.to_string())?
    } else {
        Vec::new()
    };

    groups.push(group);

    let json = serde_json::to_string_pretty(&groups).map_err(|e| e.to_string())?;
    fs::write(&file_path, json).map_err(|e| e.to_string())?;

    Ok(())
}

#[tauri::command]
fn delete_group(id: String) -> Result<(), String> {
    let data_dir = if cfg!(debug_assertions) { get_base_dir().join("../data") } else { get_base_dir().join("data") };
    let file_path = data_dir.join("groups.json");

    if !file_path.exists() {
        return Err("Groups file does not exist".to_string());
    }

    let content = fs::read_to_string(&file_path).map_err(|e| e.to_string())?;
    let mut groups: Vec<Group> = serde_json::from_str(&content).map_err(|e| e.to_string())?;

    groups.retain(|group| group.id != id);

    let json = serde_json::to_string_pretty(&groups).map_err(|e| e.to_string())?;
    fs::write(&file_path, json).map_err(|e| e.to_string())?;

    Ok(())
}

#[tauri::command]
fn get_groups() -> Result<Vec<Group>, String> {
    let data_dir = if cfg!(debug_assertions) { get_base_dir().join("../data") } else { get_base_dir().join("data") };
    let file_path = data_dir.join("groups.json");

    if !file_path.exists() {
        return Ok(Vec::new());
    }

    let content = fs::read_to_string(&file_path).map_err(|e| e.to_string())?;
    let groups: Vec<Group> = serde_json::from_str(&content).map_err(|e| e.to_string())?;

    Ok(groups)
}

#[tauri::command]
async fn get_group_metrics(id: String, time_frame: u64) -> Result<String, String> {
    let data_dir = if cfg!(debug_assertions) { get_base_dir().join("../data") } else { get_base_dir().join("data") };
    let file_path = data_dir.join("groups.json");

    if !file_path.exists() {
        return Err("Groups file does not exist".to_string());
    }

    let content = fs::read_to_string(&file_path).map_err(|e| e.to_string())?;
    let groups: Vec<Group> = serde_json::from_str(&content).map_err(|e| e.to_string())?;

    let group = groups.into_iter().find(|group| group.id == id).ok_or_else(|| "Group not found".to_string())?;

    let script_dir = if cfg!(debug_assertions) { get_base_dir().join("../../backend") } else { get_base_dir().join("backend") };

    let mut cmd = std::process::Command::new("python");
    cmd.arg(script_dir.join("main.py"))
        .arg(&group.grafana_url)
        .arg(&format!("{}h", time_frame))
        .arg(&id);

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
    }

    let output = cmd.output().map_err(|e| e.to_string())?;

    let output_str = String::from_utf8_lossy(&output.stdout);
    let output_json: Value = serde_json::from_str(&output_str).map_err(|e| e.to_string())?;
    if let Some(session) = output_json.get("grafana_session") {
        fetch_grafana_logs(session.as_str().unwrap_or("").to_string(), group, time_frame).await
    } else if let Some(error) = output_json.get("error") {
        Err(error.as_str().unwrap_or("Unknown error").to_string())
    } else {
        Err("Unexpected output from backend".to_string())
    }
}

#[tauri::command]
async fn fetch_grafana_logs(session_cookie: String, group: Group, time_frame: u64) -> Result<String, String> {
    let mut log_groups: HashMap<String, HashMap<String, LogCount>> = HashMap::from([
        ("API Errors".to_string(), HashMap::new()),
        ("Publisher Errors".to_string(), HashMap::new()),
        ("Worker Errors".to_string(), HashMap::new()),
        ("DLQ Errors".to_string(), HashMap::new()), // Won't touch this
        ("Slow Queries".to_string(), HashMap::new()),
        ("Timeouts".to_string(), HashMap::new()),
        ("Other Errors (Maintenance tasks etc)".to_string(), HashMap::new()),
        ("500 Responses".to_string(), HashMap::new()),
    ]);

    let to: String = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_millis()
        .to_string();
    let from: String = (SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_millis() - (time_frame * ONE_HOUR_IN_MILLIS) as u128)
        .to_string();
    let client = reqwest::Client::new();

    let queries: HashMap<&str, String> = HashMap::from([
        ("", group.errors), // Leave as Generic errors for now 
        ("Timeouts", group.timeouts), 
        ("Slow Queries", group.slow_queries), 
        ("500 Responses", group.five_hundreds) 
    ]);

    // The conditional below is a hack to get the correct datasource UID. 
    // 4 == Sandbox == 000000006, 
    // 5 == Production == 000000007. 
    let mut uid = "".to_string();
    if group.grafana_url.ends_with("4") {
        uid = "000000006".to_string();
    } else if group.grafana_url.ends_with("5") {
        uid = "000000007".to_string();
    }
    for (query_name, query) in queries.iter() {
        let body = serde_json::json!({
            "queries": [{
                "alias": "",
                "bucketAggs": [],
                "datasource": {"type": "elasticsearch", "uid": uid},
                "metrics": [{"id": "1", "type": "logs", "settings": {"limit": "10000"}}],
                "query": query,
                "refId": "A",
                "timeField": "Timestamp",
                "datasourceId": 7,
                "intervalMs": 30000,
                "maxDataPoints": 2346
            }],
            "from": &from,
            "to": &to
        });

        let response = client
            .post(DS_QUERY_ENDPOINT)
            .header("Content-Type", "application/json")
            .header("Cookie", format!("grafana_session={}", &session_cookie))
            .json(&body)
            .send()
            .await
            .map_err(|e| e.to_string())?;

        println!("Response status: {}", response.status());

        let json: Value = response.json().await.map_err(|e| e.to_string())?;

        if json.get("message").is_some() {
            return Err(json["message"].as_str().unwrap_or("Unknown error").to_string());
        }

        // Will return Value::Null enum if nothing, I think.
        // This, and clean_data function need more error handling most likely.
        let values = &json["results"]["A"]["frames"][0]["data"]["values"];

        let cleaned_logs: Vec<Log> = clean_data(values.as_array().unwrap_or(&vec![]))?;

        let log_counts = count_unique_logs(&cleaned_logs)?;

        // This will add each log to its own group as:
        // e.g.
        // "API Errors": {
        //     "Error message 1": { source: "source1", count: 5 },
        //     "Error message 2": { source: "source2", count: 3 },
        //     ...
        // }

        // If group found, add it to it, unless its an error type
        if let Some(log_group) = log_groups.get_mut(*query_name) {
            for (log, log_count) in log_counts {
                log_group.insert(log, log_count);
            }
        } else {
            for (error_message, error_log) in log_counts.iter() {
                let source_type = error_log.source
                    .split("/")
                    .last()
                    .ok_or("Failed to get mutable reference")?;

                if source_type == "API" {
                    log_groups
                        .get_mut("API Errors")
                        .ok_or("Failed to get mutable reference")?
                        .insert(error_message.clone(), error_log.clone());
                } else if source_type == "publisher" {
                    log_groups
                        .get_mut("Publisher Errors")
                        .ok_or("Failed to get mutable reference")?
                        .insert(error_message.clone(), error_log.clone());
                } else if source_type == "worker" || source_type == "worker-async-cmd" {
                    log_groups
                        .get_mut("Worker Errors")
                        .ok_or("Failed to get mutable reference")?
                        .insert(error_message.clone(), error_log.clone());
                } else {
                    log_groups
                        .get_mut("Other Errors (Maintenance tasks etc)")
                        .ok_or("Failed to get mutable reference")?
                        .insert(error_message.clone(), error_log.clone());
                }
            }
        }
    }

    format_logs(log_groups)
}

// Hashmap<GroupName, Hashmap<Message, {source, count}>>
fn format_logs(log_groups: HashMap<String, HashMap<String, LogCount>>) -> Result<String, String> {
    let ordered_keys: Vec<String> = vec![
        "API Errors".to_string(),
        "Publisher Errors".to_string(),
        "Worker Errors".to_string(),
        "DLQ Errors".to_string(),
        "Slow Queries".to_string(),
        "Timeouts".to_string(),
        "Other Errors (Maintenance tasks etc)".to_string(),
        "500 Responses".to_string(),
    ];

    let mut formatted_logs = String::new();
    for group_name in ordered_keys {
        formatted_logs.push_str(&format!("{}:\n", group_name));

        let logs = log_groups
            .get(&group_name)
            .ok_or("Failed to get logs for group")?;

        if logs.is_empty() {
            formatted_logs.push_str("N/A\n");
            continue;
        }

        for (log_message, log_count) in logs {
            formatted_logs.push_str(&format!(
                "{}x `{}`\n",
                log_count.count, log_message
            ));
        }
    }

    Ok(formatted_logs)
}

fn count_unique_logs(data: &Vec<Log>) -> Result<HashMap<String, LogCount>, String> {
    let mut log_counts: HashMap<String, LogCount> = HashMap::new();
    for log in data {
        if log_counts.contains_key(&log.log) {
            let log_count = log_counts.get_mut(&log.log).ok_or("Failed to get mutable reference")?;
            log_count.count += 1;
        } else {
            log_counts.insert(log.log.clone(), LogCount { source: log.source.clone(), count: 1 });
        }
    }
    Ok(log_counts)
}

fn clean_data(data: &Vec<Value>) -> Result<Vec<Log>, String> {
    if data.len() < 3 {
        return Ok(vec![]);
    }

    if let Value::Null = data[1] {
        return Ok(vec![]);
    }

    if let Value::Null = data[3] {
        return Ok(vec![]);
    }

    let logs_binding = vec![];
    let source_binding = vec![];
    let logs = &data[1].as_array().unwrap_or(&logs_binding);
    let source = &data[3].as_array().unwrap_or(&source_binding);

    let mut cleaned_logs: Vec<Log> = Vec::new();
    for i in 0..logs.len() {
        if let Some(log) = logs.get(i) {
            if let Some(source_value) = source.get(i) {
                cleaned_logs.push(Log {
                    log: clean_log_message(log.as_str().unwrap_or("").to_string())?,
                    source: source_value.as_str().unwrap_or("").to_string(),
                });
            }
        }
    }
    
    Ok(cleaned_logs)
}

fn clean_log_message(log: String) -> Result<String, String> {
    let guid_re = regex::Regex::new(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
        .map_err(|e| e.to_string())?;
    let auth0_re = regex::Regex::new(r"[0-9a-fA-F]{3}-[0-9a-fA-F]{2}-[0-9a-fA-F]{3}-[0-9a-fA-F]{2}-[0-9a-fA-F]{3}")
        .map_err(|e| e.to_string())?;

    let mut cleaned_log = guid_re.replace_all(&log, "<GUID>").to_string();
    cleaned_log = auth0_re.replace_all(&cleaned_log, "<AUTH0_TOKEN>").to_string();

    if cleaned_log.len() > MAX_KEY_LEN {
        cleaned_log = cleaned_log[..MAX_KEY_LEN].to_string();
    }

    Ok(cleaned_log)
}

#[tauri::command]
fn read_screenshot(group_id: String) -> Result<String, String> {
    let data_dir = if cfg!(debug_assertions) { get_base_dir().join("../../data/screenshots") } else { get_base_dir().join("data/screenshots") };

    // Find the latest screenshot for this group
    let entries = fs::read_dir(&data_dir).map_err(|e| e.to_string())?;
    let mut latest: Option<PathBuf> = None;
    for entry in entries {
        let entry = entry.map_err(|e| e.to_string())?;
        let name = entry.file_name().to_string_lossy().to_string();
        if name.starts_with(&format!("{}_", group_id)) && name.ends_with(".png") {
            match &latest {
                Some(prev) => {
                    if entry.path() > *prev {
                        latest = Some(entry.path());
                    }
                }
                None => latest = Some(entry.path()),
            }
        }
    }

    let path = latest.ok_or("No screenshot found for this group")?;
    let bytes = fs::read(&path).map_err(|e| e.to_string())?;
    use base64::Engine;
    Ok(base64::engine::general_purpose::STANDARD.encode(&bytes))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(
            tauri_plugin_log::Builder::new()
                .level(tauri_plugin_log::log::LevelFilter::Error)
                .build(),
        )
        .invoke_handler(tauri::generate_handler![
            append_group,
            delete_group,
            get_groups,
            get_group_metrics,
            read_screenshot
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
