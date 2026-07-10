import { useState } from "react";
import { CreateGroup } from "../CreateGroup/CreateGroup";
import "./Dashboard.css";

function Dashboard() {
  const [isAddingGroup, setIsAddingGroup] = useState(false);

  return (
    <div className="dashboard">
      { isAddingGroup && 
        <CreateGroup setIsAddingGroup={setIsAddingGroup} />
      }
      { !isAddingGroup && <button onClick={() => setIsAddingGroup(true)}>
        plus_sign_placeholder
      </button>}
    </div>
  );
}

export { Dashboard };