import { useState } from "react";
import ReactMarkdown from "react-markdown";
import api from "../api/api";

export default function SearchBox() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const research = async () => {
    if (!topic.trim()) {
      alert("Please enter a research topic.");
      return;
    }

    try {
      setLoading(true);

      const response = await api.post("/research", {
        topic: topic,
      });

      setResult(response.data);
    } catch (error) {
      console.error(error);
      alert("Failed to fetch research.");
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
          style={{
            padding: "14px 24px",
            backgroundColor: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "16px",
          }}
        >
          {loading ? "Researching..." : "Research"}
        </button>
      </div>

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
          <h2 style={{ marginBottom: "20px" }}>
            📄 Executive Summary
          </h2>

          <div
            style={{
              textAlign: "left",
              lineHeight: "1.8",
              fontSize: "16px",
            }}
          >
            <ReactMarkdown>{result.summary}</ReactMarkdown>
          </div>

          <hr style={{ margin: "30px 0" }} />

          <h2>🔗 Sources</h2>

          <div style={{ marginTop: "20px" }}>
            {result.sources.map((source, index) => (
              <div
                key={index}
                style={{
                  padding: "15px",
                  marginBottom: "12px",
                  border: "1px solid #444",
                  borderRadius: "10px",
                  backgroundColor: "#2b2b2b",
                }}
              >
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: "#4ea8ff",
                    textDecoration: "none",
                    fontWeight: "bold",
                    fontSize: "16px",
                  }}
                >
                  {source.title}
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}