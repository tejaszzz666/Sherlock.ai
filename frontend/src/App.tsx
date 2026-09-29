import { useState } from "react";
import { Navigation } from "./components/Navigation";
import { Hero } from "./components/Hero";
import { ImageDetection } from "./components/ImageDetection";
import { VideoDetection } from "./components/VideoDetection";
import { About } from "./components/About";

type Page = "home" | "image" | "video" | "about";

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>("home");

  const handleNavigate = (page: string) => {
    setCurrentPage(page as Page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-[#0b0b0b] text-white">
      <Navigation currentPage={currentPage} onNavigate={handleNavigate} />

      {currentPage === "home" && <Hero onNavigate={handleNavigate} />}
      {currentPage === "image" && <ImageDetection />}
      {currentPage === "video" && <VideoDetection />}
      {currentPage === "about" && <About />}
    </div>
  );
}
