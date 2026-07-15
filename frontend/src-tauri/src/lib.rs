use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Serialize, Deserialize)]
struct Group {
    id: String,
    grafana_url: String,
    errors: String,
    timeouts: String,
    slow_queries: String,
    five_hundreds: String,
}

#[tauri::command]
fn append_group(group: Group) -> Result<(), String> {
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../data");
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
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../data");
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
    let data_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../data");
    let file_path = data_dir.join("groups.json");

    if !file_path.exists() {
        return Ok(Vec::new());
    }

    let content = fs::read_to_string(&file_path).map_err(|e| e.to_string())?;
    let groups: Vec<Group> = serde_json::from_str(&content).map_err(|e| e.to_string())?;

    Ok(groups)
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
            get_groups
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
