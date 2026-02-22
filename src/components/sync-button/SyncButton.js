import { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { pushLists, pullLists } from "../../utils/firebase";
import { setLists } from "../../state/lists";

export const SyncButton = () => {
  const dispatch = useDispatch();
  const lists = useSelector((state) => state.lists);
  const [status, setStatus] = useState("idle");

  const handlePush = async () => {
    setStatus("saving");
    await pushLists(lists);
    const syncId = localStorage.getItem("owb.syncId");
    alert(`Lists saved! Your Sync Code: ${syncId}`);
    setStatus("idle");
  };

  const handlePull = async () => {
    const code = prompt("Enter your Sync Code from another device:");
    if (!code) return;
    localStorage.setItem("owb.syncId", code);
    setStatus("loading");
    const remoteLists = await pullLists();
    if (remoteLists) {
      localStorage.setItem("owb.lists", JSON.stringify(remoteLists));
      dispatch(setLists(remoteLists));
      alert("Lists synced successfully!");
    } else {
      alert("No lists found for that code.");
    }
    setStatus("idle");
  };

  return (
    <div>
      <button onClick={handlePush} disabled={status !== "idle"}>☁️ Save to Cloud</button>
      <button onClick={handlePull} disabled={status !== "idle"}>📥 Load from Cloud</button>
    </div>
  );
};
