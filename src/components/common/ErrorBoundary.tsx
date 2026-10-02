import React, { Component, type ErrorInfo, type ReactNode } from "react";

type Props = {
  children: ReactNode;
};

type State = {
  hasError: boolean;
  error?: Error;
};

class ErrorBoundary extends Component<Props, State> {
  state: State = {
    hasError: false,
  };

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("VeriLens UI Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <main
          style={{
            minHeight: "100vh",
            display: "grid",
            placeItems: "center",
            padding: "40px",
            background: "#F7F5F0",
            color: "#1C1C1A",
            fontFamily: "Arial, sans-serif",
          }}
        >
          <div style={{ maxWidth: "600px" }}>
            <p
              style={{
                fontSize: "12px",
                letterSpacing: "3px",
                fontWeight: 700,
              }}
            >
              VERILENS
            </p>

            <h1>Something went wrong.</h1>

            <p style={{ color: "#6F7168", lineHeight: 1.6 }}>
              The application encountered an unexpected error.
            </p>

            {this.state.error && (
              <pre
                style={{
                  marginTop: "24px",
                  padding: "16px",
                  overflow: "auto",
                  background: "#ECEAE4",
                  borderRadius: "12px",
                  fontSize: "13px",
                }}
              >
                {this.state.error.message}
              </pre>
            )}

            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: "24px",
                padding: "12px 18px",
                border: "none",
                borderRadius: "10px",
                background: "#1C1C1A",
                color: "#fff",
                cursor: "pointer",
              }}
            >
              Reload VeriLens
            </button>
          </div>
        </main>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;