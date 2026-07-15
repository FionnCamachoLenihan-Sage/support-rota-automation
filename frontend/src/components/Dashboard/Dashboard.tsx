import { useEffect, useState } from "react";
import { CreateGroup } from "../CreateGroup/CreateGroup";
import "./Dashboard.css";
import { invoke } from "@tauri-apps/api/core";
import { Group } from "../Group/Group";

export type IGroup = {
  id: String;
  grafana_url: String;
  errors: String;
  timeouts: String;
  slow_queries: String;
  five_hundreds: String;
};

function Dashboard() {
  const [isAddingGroup, setIsAddingGroup] = useState(false);

  const [groups, setGroups] = useState<IGroup[]>([]);

  useEffect(() => {
    invoke("get_groups").then((fetchedGroups) => {
      setGroups(fetchedGroups as IGroup[]);
    });
  }, []);

  return (
    <div className="dashboard">
      <div className="groups">
        {groups.map((group) => (
          <Group
            key={group.id.toString()}
            group={group}
            setGroups={setGroups}
          />
        ))}
      </div>

      {isAddingGroup && <CreateGroup setIsAddingGroup={setIsAddingGroup} />}

      {!isAddingGroup && (
        <button className="add-button" onClick={() => setIsAddingGroup(true)}>
          Add Query Group
        </button>
      )}
    </div>
  );
}

export { Dashboard };
