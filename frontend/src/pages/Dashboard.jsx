import { useState } from "react";
import Navbar from "../components/Navbar";
import SearchBox from "../components/SearchBox";
import History from "./History";

export default function Dashboard() {
  const [view, setView] = useState("search");

  return (
    <div
      style={{
        maxWidth: "1100px",
        margin: "40px auto",
        padding: "20px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1>🚀 Enterprise AI Research Agent</h1>

      <p>
        AI-powered research assistant using FastAPI, PostgreSQL, ChromaDB and
        Gemini.
      </p>

      <Navbar view={view} onChangeView={setView} />

      {view === "search" && <SearchBox />}
      {view === "history" && <History />}
    </div>
  );
}
