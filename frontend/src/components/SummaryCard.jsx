const CLASSIFICATION_COLORS = {
  benefit: "#1f8a4c",
  challenge: "#c0392b",
  risk: "#c0392b",
  trend: "#2563eb",
  statistic: "#8e44ad",
  other: "#555",
};

function FindingRow({ finding, highlighted }) {
  const color = CLASSIFICATION_COLORS[finding.classification] || CLASSIFICATION_COLORS.other;
  return (
    <div
      style={{
        padding: "10px 12px",
        marginBottom: "8px",
        borderRadius: "8px",
        border: highlighted ? `1px solid ${color}` : "1px solid #3a3a3a",
        backgroundColor: "#232323",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", gap: "10px" }}>
        <span style={{ fontSize: "14px", lineHeight: "1.5" }}>{finding.content}</span>
        <span
          style={{
            flexShrink: 0,
            fontSize: "11px",
            fontWeight: "bold",
            color,
            textTransform: "uppercase",
          }}
        >
          {finding.classification}
        </span>
      </div>
      <SourceLine source={finding.source} confidence={finding.confidence} />
    </div>
  );
}

function SourceLine({ source, confidence }) {
  return (
    <div style={{ fontSize: "12px", color: "#999", marginTop: "6px" }}>
      <a href={source.url} target="_blank" rel="noopener noreferrer" style={{ color: "#4ea8ff" }}>
        {source.title}
      </a>
      {" · confidence " + Math.round(confidence * 100) + "%"}
    </div>
  );
}

export default function SummaryCard({ question }) {
  const findingById = Object.fromEntries(question.findings.map((f) => [f.id, f]));

  return (
    <div
      style={{
        border: "1px solid #444",
        borderRadius: "12px",
        padding: "18px 20px",
        marginBottom: "18px",
        backgroundColor: "#1e1e1e",
      }}
    >
      <h3 style={{ marginTop: 0, marginBottom: "10px" }}>{question.text}</h3>

      <div
        style={{
          padding: "12px 14px",
          borderRadius: "8px",
          backgroundColor: "#16311f",
          border: "1px solid #1f8a4c",
          marginBottom: "14px",
          fontSize: "14px",
          lineHeight: "1.6",
        }}
      >
        <strong>Conclusion:</strong> {question.conclusion.summary}
      </div>

      <div style={{ fontSize: "13px", color: "#aaa", marginBottom: "8px" }}>
        Findings ({question.findings.length})
      </div>
      {question.findings.map((f) => (
        <FindingRow
          key={f.id}
          finding={f}
          highlighted={question.conclusion.supporting_finding_ids.includes(f.id)}
        />
      ))}

      {question.contradictions.length > 0 && (
        <div style={{ marginTop: "14px" }}>
          <div style={{ fontSize: "13px", color: "#e67e22", marginBottom: "8px" }}>
            ⚠ Contradictions detected ({question.contradictions.length})
          </div>
          {question.contradictions.map((c, i) => (
            <div
              key={i}
              style={{
                padding: "10px 12px",
                marginBottom: "8px",
                borderRadius: "8px",
                border: "1px solid #e67e22",
                backgroundColor: "#2a1f14",
                fontSize: "13px",
                lineHeight: "1.5",
              }}
            >
              <div>{c.explanation}</div>
              <div style={{ color: "#999", marginTop: "6px", fontSize: "12px" }}>
                Finding #{c.finding_a_id} ("{findingById[c.finding_a_id]?.content}") vs. Finding #{c.finding_b_id} ("{findingById[c.finding_b_id]?.content}")
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
