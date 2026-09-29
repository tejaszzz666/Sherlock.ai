// Debug version of main.tsx
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

console.log("🔍 Sherlock.ai - Starting application...");

const rootElement = document.getElementById("root");

if (!rootElement) {
  console.error("❌ ERROR: Root element not found!");
} else {
  console.log("✅ Root element found");
  try {
    createRoot(rootElement).render(<App />);
    console.log("✅ React app rendered successfully");
  } catch (error) {
    console.error("❌ ERROR rendering React app:", error);
  }
}
