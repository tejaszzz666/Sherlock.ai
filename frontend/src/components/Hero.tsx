import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Scan, Video } from "lucide-react";

interface HeroProps {
  onNavigate: (page: string) => void;
}

export function Hero({ onNavigate }: HeroProps) {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setLoaded(true);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background with subtle texture */}
      <div className="absolute inset-0 bg-[#0b0b0b]">
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1653104877761-181b3977808e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkYXJrJTIwYWJzdHJhY3QlMjB0ZXh0dXJlfGVufDF8fHx8MTc2ODY1NzkyMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral')`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/80" />
      </div>

      {/* Animated noise overlay */}
      <div className="absolute inset-0 opacity-[0.03] mix-blend-overlay">
        <div className="absolute inset-0 animate-pulse bg-gradient-to-br from-white via-transparent to-white" />
      </div>

      {/* Content */}
      <div
        className={`relative z-10 max-w-5xl mx-auto px-6 text-center transition-all duration-1000 ${
          loaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
        }`}
      >
        <h1 className="text-7xl md:text-8xl lg:text-9xl tracking-tight mb-8 text-white">
          SHERLOCK.AI
        </h1>

        <p className="text-xl md:text-2xl lg:text-3xl mb-6 text-gray-300 tracking-wide">
          AI that watches AI
        </p>

        <p className="text-base md:text-lg lg:text-xl max-w-3xl mx-auto mb-16 text-gray-400 leading-relaxed">
          Detect deepfakes, manipulated media, and synthetic content with
          forensic-level intelligence.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
          <Button
            onClick={() => onNavigate("image")}
            size="lg"
            className="bg-white text-black hover:bg-gray-200 transition-all duration-300 px-12 py-7 text-lg tracking-wide min-w-[200px]"
          >
            <Scan className="mr-3 h-5 w-5" />
            Detect Image
          </Button>
          <Button
            onClick={() => onNavigate("video")}
            size="lg"
            variant="outline"
            className="border-white/20 text-white hover:bg-white/10 hover:border-white/40 transition-all duration-300 px-12 py-7 text-lg tracking-wide min-w-[200px]"
          >
            <Video className="mr-3 h-5 w-5" />
            Detect Video
          </Button>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0b0b0b] to-transparent" />
    </section>
  );
}
