import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import "./CreateGroup.css";
import { invoke } from "@tauri-apps/api/core";

function CreateGroup({
  setIsAddingGroup,
}: {
  setIsAddingGroup: (isAdding: boolean) => void;
}) {
  const [grafanaUrl, setGrafanaUrl] = useState("");
  const [errors, setErrors] = useState("");
  const [timeouts, setTimeouts] = useState("");
  const [slowQueries, setSlowQueries] = useState("");
  const [fiveHundreds, setFiveHundreds] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const groupId = uuidv4();

    const group = {
      id: groupId,
      grafana_url: grafanaUrl,
      errors,
      timeouts,
      slow_queries: slowQueries,
      five_hundreds: fiveHundreds,
    };

    await invoke("append_group", { group });

    setIsAddingGroup(false);
  };

  return (
    <div className="create-group">
      <form className="create-group-form" onSubmit={handleSubmit}>
        <div>
          <p>Enter your Grafana URL:</p>
          <input
            type="text"
            value={grafanaUrl}
            onChange={(e) => setGrafanaUrl(e.target.value)}
          />
        </div>
        <div>
          <p>Errors:</p>
          <input
            type="text"
            value={errors}
            onChange={(e) => setErrors(e.target.value)}
          />
        </div>
        <div>
          <p>Timeouts:</p>
          <input
            type="text"
            value={timeouts}
            onChange={(e) => setTimeouts(e.target.value)}
          />
        </div>
        <div>
          <p>Slow Queries:</p>
          <input
            type="text"
            value={slowQueries}
            onChange={(e) => setSlowQueries(e.target.value)}
          />
        </div>
        <div>
          <p>500s:</p>
          <input
            type="text"
            value={fiveHundreds}
            onChange={(e) => setFiveHundreds(e.target.value)}
          />
        </div>
        <div className="create-group-buttons">
          <button className="create-button" type="submit">
            Create Group
          </button>
          <button
            className="cancel-button"
            type="button"
            onClick={() => setIsAddingGroup(false)}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export { CreateGroup };
