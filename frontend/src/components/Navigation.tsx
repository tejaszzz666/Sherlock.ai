import { useState, useEffect } from "react";

interface NavigationProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export function Navigation({ currentPage, onNavigate }: NavigationProps) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled
          ? "bg-black/40 backdrop-blur-xl border-b border-white/10"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 lg:px-12">
        <div className="flex items-center justify-between h-20">
          <button
            onClick={() => onNavigate("home")}
            className="text-xl tracking-wider hover:opacity-70 transition-opacity"
          >
            SHERLOCK.AI
          </button>

          <div className="flex items-center gap-8">
            <button
              onClick={() => onNavigate("image")}
              className={`text-sm tracking-wide hover:text-white transition-colors ${
                currentPage === "image" ? "text-white" : "text-gray-400"
              }`}
            >
              Image
            </button>
            <button
              onClick={() => onNavigate("video")}
              className={`text-sm tracking-wide hover:text-white transition-colors ${
                currentPage === "video" ? "text-white" : "text-gray-400"
              }`}
            >
              Video
            </button>
            <button
              onClick={() => onNavigate("about")}
              className={`text-sm tracking-wide hover:text-white transition-colors ${
                currentPage === "about" ? "text-white" : "text-gray-400"
              }`}
            >
              About
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
