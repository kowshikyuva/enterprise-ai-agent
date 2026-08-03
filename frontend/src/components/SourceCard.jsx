export default function SourceCard({ source }) {
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        display: "block",
        color: "#4ea8ff",
        textDecoration: "none",
        fontSize: "13px",
        marginTop: "6px",
      }}
    >
      🔗 {source.title}
    </a>
  );
}
