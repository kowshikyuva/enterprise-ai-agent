import { useState } from "react";
import ReactMarkdown from "react-markdown";
import api from "../api/api";
import SummaryCard from "./SummaryCard";
import StatsCard from "./StatsCard";

export default function SearchBox() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const research = async () => {
    if (!topic.trim()) {
      alert("Please enter a research topic.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // The pipeline runs synchronously: define questions -> search -> scrape
      // -> extract findings -> compare/classify -> detect contradictions ->
      // conclude, per question. This can take a while for multiple questions.
      const response = await api.post("/research", { topic });

      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to run the research pipeline. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginTop: "30px" }}>
      <div style={{ display: "flex", gap: "10px" }}>
        <input
          type="text"
          value={topic}
          placeholder="Enter research topic..."
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && research()}
          style={{
            flex: 1,
            padding: "14px",
            fontSize: "16px",
            borderRadius: "8px",
            border: "1px solid #ccc",
          }}
        />

        <button
          onClick={research}
          disabled={loading}
          style={{
            padding: "14px 24px",
            backgroundColor: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: loading ? "default" : "pointer",
            fontSize: "16px",
            opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? "Researching..." : "Research"}
        </button>
      </div>

      {error && (
        <div style={{ marginTop: "16px", color: "#e74c3c" }}>{error}</div>
      )}

      {result && (
        <div
          style={{
            marginTop: "30px",
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
