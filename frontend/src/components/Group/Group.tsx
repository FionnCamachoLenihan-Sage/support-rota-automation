import { invoke } from "@tauri-apps/api/core";
import { error as tauri_error } from "@tauri-apps/plugin-log";
import "./Group.css";
import { IGroup } from "../Dashboard/Dashboard";

type GroupProps = {
  group: IGroup;
  setGroups: React.Dispatch<React.SetStateAction<IGroup[]>>;
};

function Group({ group, setGroups }: GroupProps) {
  const { id, grafana_url, errors, timeouts, slow_queries, five_hundreds } =
    group;

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

  return (
    <div className="group">
      <h2>{id}</h2>
      <div>
        <p>Grafana URL: </p>
        <p>{grafana_url}</p>
      </div>
      <div>
        <p>Errors: </p>
        <p>{errors}</p>
      </div>
      <div>
        <p>Timeouts: </p>
        <p>{timeouts}</p>
      </div>
      <div>
        <p>Slow Queries: </p>
        <p>{slow_queries}</p>
      </div>
      <div>
        <p>500s: </p>
        <p>{five_hundreds}</p>
      </div>
      <button className="delete-button" onClick={handleDeleteGroup}>
        Delete Group
      </button>
    </div>
  );
}

export { Group };
