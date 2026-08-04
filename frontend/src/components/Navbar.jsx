export default function Navbar({ view, onChangeView }) {
  const tabs = [
    { id: "search", label: "🔍 Research" },
    { id: "history", label: "🕘 History" },
  ];

  return (
    <div
      style={{
        display: "flex",
        gap: "8px",
        marginBottom: "20px",
        borderBottom: "1px solid #333",
        paddingBottom: "0",
      }}
    >
      {tabs.map((tab) => {
        const active = view === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChangeView(tab.id)}
            style={{
              padding: "10px 18px",
              fontSize: "15px",
              fontWeight: active ? "bold" : "normal",
              background: "none",
              border: "none",
              borderBottom: active ? "3px solid #2563eb" : "3px solid transparent",
              color: active ? "#2563eb" : "inherit",
              cursor: "pointer",
              marginBottom: "-1px",
            }}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
