import { useState } from "react";
import "./CreateGroup.css";
import { invoke } from "@tauri-apps/api/core";
import { IGroup } from "../Dashboard/Dashboard";

type CreateGroupProps = {
  setIsAddingGroup: (isAdding: boolean) => void;
  setGroups: React.Dispatch<React.SetStateAction<IGroup[]>>;
};

function CreateGroup({ setIsAddingGroup, setGroups }: CreateGroupProps) {
  const [groupName, setGroupName] = useState("");
  const [grafanaUrl, setGrafanaUrl] = useState("");
  const [errors, setErrors] = useState("");
  const [timeouts, setTimeouts] = useState("");
  const [slowQueries, setSlowQueries] = useState("");
  const [fiveHundreds, setFiveHundreds] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const groupId = crypto.randomUUID();

    const group = {
      group_name: groupName,
      id: groupId,
      grafana_url: grafanaUrl,
      errors,
      timeouts,
      slow_queries: slowQueries,
      five_hundreds: fiveHundreds,
    };

    await invoke("append_group", { group });

    setIsAddingGroup(false);
    setGroups((prevGroups) => [...prevGroups, group]);
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
          <p>Enter your Group Name:</p>
          <input
            type="text"
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
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
