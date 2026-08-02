import SearchBox from "../components/SearchBox";

export default function Dashboard() {
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

      <SearchBox />
    </div>
  );
}