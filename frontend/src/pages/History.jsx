import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import api from "../api/api";
import SummaryCard from "../components/SummaryCard";
import StatsCard from "../components/StatsCard";

export default function History() {
  const [projects, setProjects] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [listError, setListError] = useState(null);

  const [selectedId, setSelectedId] = useState(null);
  const [result, setResult] = useState(null);
  const [loadingResult, setLoadingResult] = useState(false);
  const [resultError, setResultError] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoadingList(true);
      setListError(null);
      const response = await api.get("/projects");
      setProjects(response.data);
    } catch (err) {
      console.error(err);
      setListError("Couldn't load history. Is the backend running?");
    } finally {
      setLoadingList(false);
    }
  };

  const openProject = async (id) => {
    try {
      setSelectedId(id);
      setLoadingResult(true);
      setResultError(null);
      setResult(null);

      // Pulls the stored run straight from the knowledge base -- no
      // pipeline re-run, no Gemini calls, so this always works even if
      // the day's LLM quota is exhausted.
      const response = await api.get(`/research/${id}`);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setResultError("Couldn't load this run.");
    } finally {
      setLoadingResult(false);
    }
  };

  const backToList = () => {
    setSelectedId(null);
    setResult(null);
    setResultError(null);
  };

  if (selectedId) {
    return (
      <div>
        <button
          onClick={backToList}
          style={{
            padding: "8px 16px",
            marginBottom: "16px",
            background: "none",
            border: "1px solid #444",
            borderRadius: "8px",
            color: "inherit",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          ← Back to history
        </button>

        {loadingResult && <p>Loading saved run...</p>}
        {resultError && <p style={{ color: "#e74c3c" }}>{resultError}</p>}

        {result && (
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: "12px",
              padding: "25px",
              backgroundColor: "#1e1e1e",
              color: "#ffffff",
            }}
          >
            <h2 style={{ marginTop: 0 }}>🚀 {result.topic}</h2>

            <StatsCard
              totalSources={result.total_sources}
              questionCount={result.questions.length}
              status={result.status}
            />

            <h3>🧩 Research Questions & Evidence Trail</h3>
            {result.questions.map((q) => (
              <SummaryCard key={q.id} question={q} />
            ))}

            <hr style={{ margin: "30px 0" }} />

            <h2>📄 Executive Summary</h2>
            <div style={{ textAlign: "left", lineHeight: "1.8", fontSize: "16px" }}>
              <ReactMarkdown>{result.final_report}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Past research runs</h2>
      <p style={{ color: "#999", marginTop: "-8px" }}>
        Pulled straight from the stored knowledge base — click one to reopen it, no re-run needed.
      </p>

      {loadingList && <p>Loading history...</p>}
      {listError && <p style={{ color: "#e74c3c" }}>{listError}</p>}

      {!loadingList && !listError && projects.length === 0 && (
        <p style={{ color: "#999" }}>No research runs yet. Run a topic from the Research tab first.</p>
      )}

      {projects.map((p) => (
        <div
          key={p.id}
          onClick={() => openProject(p.id)}
          style={{
            padding: "16px 20px",
            marginBottom: "12px",
            borderRadius: "10px",
            border: "1px solid #444",
            backgroundColor: "#232323",
            cursor: "pointer",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: "16px", fontWeight: "bold", marginBottom: "4px" }}>
              {p.topic}
            </div>
            <div style={{ fontSize: "13px", color: "#999" }}>
              {p.question_count} question{p.question_count === 1 ? "" : "s"} ·{" "}
              {new Date(p.created_at).toLocaleString()}
            </div>
          </div>
          <span
            style={{
              padding: "4px 12px",
              borderRadius: "999px",
              fontSize: "12px",
              fontWeight: "bold",
              backgroundColor: p.status === "completed" ? "#1f8a4c" : "#555",
              color: "white",
              flexShrink: 0,
              marginLeft: "12px",
            }}
          >
            {p.status}
          </span>
        </div>
      ))}
    </div>
  );
}
