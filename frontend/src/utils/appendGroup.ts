import { invoke } from "@tauri-apps/api/core";

interface Group {
  id: string;
  grafana_url: string;
  errors: string;
  timeouts: string;
  slow_queries: string;
  five_hundreds: string;
}

async function appendGroup(group: Group): Promise<void> {
  await invoke("append_group", { group });
}

export { appendGroup };
export type { Group };