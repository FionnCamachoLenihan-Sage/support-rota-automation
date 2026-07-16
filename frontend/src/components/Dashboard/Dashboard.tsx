import { useEffect, useState } from "react";
import { CreateGroup } from "../CreateGroup/CreateGroup";
import "./Dashboard.css";
import { invoke } from "@tauri-apps/api/core";
import { Group } from "../Group/Group";

export type IGroup = {
  group_name: string;
  id: string;
  grafana_url: string;
  errors: string;
  timeouts: string;
  slow_queries: string;
  five_hundreds: string;
};

function Dashboard() {
  const [isAddingGroup, setIsAddingGroup] = useState(false);
  const [globalHours, setGlobalHours] = useState(24);

  const [groups, setGroups] = useState<IGroup[]>([]);
  const [metricsMap, setMetricsMap] = useState<Record<string, string | null>>(
    {},
  );
  const [loadingGroupIds, setLoadingGroupIds] = useState<string[]>([]);

  useEffect(() => {
    invoke("get_groups").then((fetchedGroups) => {
      setGroups(fetchedGroups as IGroup[]);
    });
  }, []);

  const handleGetGroupMetrics = async (id: string, hours: number) => {
    setLoadingGroupIds((prev) => [...prev, id.toString()]);
    await invoke("get_group_metrics", { id, timeFrame: hours })
      .then((metrics: any) => {
        setMetricsMap((prev) => ({ ...prev, [id.toString()]: metrics }));
      })
      .catch((error) => {
        console.error(`Failed to get metrics for group ${id}: ${error}`);
      });
    setLoadingGroupIds((prev) => prev.filter((gId) => gId !== id.toString()));
  };

  const handleGetAllMetrics = async () => {
    for (const group of groups) {
      await handleGetGroupMetrics(group.id, globalHours);
    }
  };

  const handleSetHours = (event: React.ChangeEvent<HTMLInputElement>) => {
    const inputElement = event.target as HTMLInputElement;
    const newHours = parseInt(inputElement.value, 10);
    if (!isNaN(newHours)) {
      setGlobalHours(newHours);
    }
  };

  return (
    <div className="dashboard">
      {isAddingGroup && (
        <CreateGroup
          setIsAddingGroup={setIsAddingGroup}
          setGroups={setGroups}
        />
      )}

      {!isAddingGroup && (
        <div className="dashboard-buttons">
          <button className="add-button" onClick={() => setIsAddingGroup(true)}>
            Add Query Group
          </button>
          <button className="all-metrics-button" onClick={handleGetAllMetrics}>
            Get All Metrics
          </button>
          <p className="hours-label">Hours: </p>
          <input
            type="text"
            placeholder="24"
            value={globalHours}
            className="hours-input"
            onChange={handleSetHours}
          />
        </div>
      )}

      <div className="groups">
        {groups.map((group) => (
          <Group
            key={group.id.toString()}
            group={group}
            setGroups={setGroups}
            metrics={metricsMap[group.id.toString()] ?? null}
            isLoading={loadingGroupIds.includes(group.id.toString())}
            onGetMetrics={(hours) => handleGetGroupMetrics(group.id, hours)}
          />
        ))}
      </div>
    </div>
  );
}

export { Dashboard };
