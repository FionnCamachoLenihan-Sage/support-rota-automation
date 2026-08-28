import { invoke } from "@tauri-apps/api/core";
import {
  error as tauri_error,
  info as tauri_info,
} from "@tauri-apps/plugin-log";
import { useState } from "react";
import "./Group.css";
import { IGroup } from "../Dashboard/Dashboard";
type GroupProps = {
  group: IGroup;
  setGroups: React.Dispatch<React.SetStateAction<IGroup[]>>;
  metrics: string | null;
  isLoading: boolean;
  onGetMetrics: (hours: number) => void;
};

function Group({
  group,
  setGroups,
  metrics,
  isLoading,
  onGetMetrics,
}: GroupProps) {
  const [hours, setHours] = useState(24);

  const {
    group_name,
    id,
    grafana_url,
    errors,
    timeouts,
    slow_queries,
    five_hundreds,
  } = group;

  const handleDeleteGroup = async () => {
    await invoke("delete_group", { id })
      .then(() => {
        setGroups((prevGroups) => prevGroups.filter((g) => g.id !== id));
      })
      .catch((error) => {
        // Handle error, e.g., show an error message
        console.error("Failed to delete group:", error);
        tauri_error(`Failed to delete group: ${error}`);
      });
  };

  const handleSetHours = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value, 10);
    if (!isNaN(value)) {
      setHours(value);
    }
  };

  const handleCopyMetricsToClipboard = async () => {
    if (metrics) {
      try {
        await navigator.clipboard.writeText(metrics);
        tauri_info("Metrics copied to clipboard");
      } catch (error) {
        tauri_error(`Failed to copy metrics to clipboard: ${error}`);
      }
    } else {
      tauri_error("No metrics available to copy");
    }
  };

  // data/screenshots/<group_id>_<timestamp>.png
  const handleCopyScreenshotToClipboard = async () => {
    try {
      const base64: string = await invoke("read_screenshot", { groupId: id });
      const byteString = atob(base64);
      const bytes = new Uint8Array(byteString.length);
      for (let i = 0; i < byteString.length; i++) {
        bytes[i] = byteString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: "image/png" });
      await navigator.clipboard.write([
        new ClipboardItem({ "image/png": blob }),
      ]);
      tauri_info("Screenshot copied to clipboard");
    } catch (error) {
      tauri_error(`Failed to copy screenshot to clipboard: ${error}`);
    }
  };

  return (
    <div className="group">
      <h2>{group_name}</h2>
      {!metrics && !isLoading ? (
        <p className="status-pill none">No metrics this session</p>
      ) : isLoading ? (
        <p className="status-pill loading">Loading...</p>
      ) : (
        <div className="button-group">
          <p className="status-pill done">Metrics available</p>
          <button
            className="copy-button"
            onClick={handleCopyMetricsToClipboard}
          >
            Copy Metrics
          </button>
          <button
            className="copy-button"
            onClick={handleCopyScreenshotToClipboard}
          >
            Copy Screenshot
          </button>
        </div>
      )}
      <div className="log-group">
        <p>Grafana URL: </p>
        <p>{grafana_url}</p>
      </div>
      <div className="log-group">
        <p>Errors: </p>
        <p>{errors}</p>
      </div>
      <div className="log-group">
        <p>Timeouts: </p>
        <p>{timeouts}</p>
      </div>
      <div className="log-group">
        <p>Slow Queries: </p>
        <p>{slow_queries}</p>
      </div>
      <div className="log-group">
        <p>500s: </p>
        <p>{five_hundreds}</p>
      </div>
      <div className="button-group">
        <button className="delete-button" onClick={handleDeleteGroup}>
          Delete Group
        </button>
        <button
          className="get-metrics-button"
          onClick={() => onGetMetrics(hours)}
        >
          Get Metrics
        </button>
        <div className="hours-input-container">
          <p>Hours: </p>
          <input
            type="text"
            placeholder="24"
            value={hours}
            className="hours-input"
            onChange={handleSetHours}
          />
        </div>
      </div>
    </div>
  );
}

export { Group };
