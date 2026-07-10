import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { appendGroup } from "../../utils/appendGroup";
import "./CreateGroup.css";

function CreateGroup({setIsAddingGroup}: {setIsAddingGroup: (isAdding: boolean) => void}) {
  const [grafanaUrl, setGrafanaUrl] = useState("");
  const [errors, setErrors] = useState("");
  const [timeouts, setTimeouts] = useState("");
  const [slowQueries, setSlowQueries] = useState("");
  const [fiveHundreds, setFiveHundreds] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const groupId = uuidv4();

    await appendGroup({
      id: groupId,
      grafana_url: grafanaUrl,
      errors,
      timeouts,
      slow_queries: slowQueries,
      five_hundreds: fiveHundreds,
    });
    
    setIsAddingGroup(false);
  };

  return (
    <div className="create-group">
      <form className="create-group-form" onSubmit={handleSubmit}>
      <label>Enter your Grafana URL:
        <input
          type="text" 
          value={grafanaUrl}
          onChange={(e) => setGrafanaUrl(e.target.value)}
        />
      </label>
      <label>Errors:
        <input
          type="text" 
          value={errors}
          onChange={(e) => setErrors(e.target.value)}
        />
      </label>
      <label>Timeouts:
        <input
          type="text" 
          value={timeouts}
          onChange={(e) => setTimeouts(e.target.value)}
        />
      </label>
      <label>Slow Queries:
        <input
          type="text" 
          value={slowQueries}
          onChange={(e) => setSlowQueries(e.target.value)}
        />
      </label>
      <label>500s:
        <input
          type="text" 
          value={fiveHundreds}
          onChange={(e) => setFiveHundreds(e.target.value)}
        />
      </label>
      <button type="submit">Create Group</button>
    </form>
    </div>
  );
};

export { CreateGroup };