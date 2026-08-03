export default function StatsCard({ totalSources, questionCount, status }) {
  const items = [
    { label: "Questions", value: questionCount },
    { label: "Sources", value: totalSources },
    { label: "Status", value: status },
  ];

  return (
    <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
      {items.map((item) => (
        <div
          key={item.label}
          style={{
            flex: 1,
            padding: "14px",
            borderRadius: "10px",
            border: "1px solid #444",
            backgroundColor: "#232323",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "20px", fontWeight: "bold" }}>{item.value}</div>
          <div style={{ fontSize: "12px", color: "#999" }}>{item.label}</div>
        </div>
      ))}
    </div>
  );
}
