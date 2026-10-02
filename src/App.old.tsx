import { Routes, Route } from "react-router-dom";

function LandingPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#F7F5F0",
        color: "#1C1C1A",
        padding: "80px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <p
        style={{
          fontSize: "12px",
          letterSpacing: "4px",
          color: "#6F7168",
          fontWeight: 700,
        }}
      >
        MULTIMODAL AI INTELLIGENCE
      </p>

      <h1
        style={{
          fontSize: "72px",
          lineHeight: 1,
          marginTop: "24px",
          marginBottom: "24px",
        }}
      >
        VeriLens
      </h1>

      <p
        style={{
          fontSize: "22px",
          color: "#6F7168",
          maxWidth: "600px",
          lineHeight: 1.6,
        }}
      >
        See beyond the content. Understand the evidence.
      </p>
    </main>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
    </Routes>
  );
}

export default App;