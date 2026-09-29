import { Shield, Scan, Activity } from "lucide-react";

export function About() {
  return (
    <div className="min-h-screen pt-32 pb-20 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-20">
          <h1 className="text-5xl md:text-6xl lg:text-7xl mb-6 tracking-tight">
            About Sherlock.ai
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
            A forensic-level AI detection system designed to identify
            AI-generated media and deepfakes with unprecedented accuracy
          </p>
        </div>

        {/* Mission */}
        <div className="mb-20">
          <div className="bg-white/[0.02] border border-white/10 rounded-lg p-12">
            <h2 className="text-3xl mb-6">Our Mission</h2>
            <p className="text-lg text-gray-300 leading-relaxed">
              Sherlock.ai is a comprehensive system designed to detect
              AI-generated media using multi-phase forensic analysis. In an era
              where synthetic content is increasingly sophisticated, we provide
              the tools needed to verify authenticity and protect against
              manipulation.
            </p>
          </div>
        </div>

        {/* Detection Phases */}
        <div className="space-y-8 mb-20">
          <h2 className="text-3xl mb-8 text-center">Detection Methodology</h2>

          <div className="bg-white/[0.02] border border-white/10 rounded-lg p-8 hover:border-white/20 transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className="bg-white/5 p-3 rounded-lg">
                <Scan className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-2xl mb-3">Phase 7: Classification</h3>
                <p className="text-gray-400 leading-relaxed">
                  Per-frame classification using deep learning models trained on
                  millions of authentic and synthetic media samples. Each frame
                  is independently analyzed for artifacts, inconsistencies, and
                  telltale signs of AI generation.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white/[0.02] border border-white/10 rounded-lg p-8 hover:border-white/20 transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className="bg-white/5 p-3 rounded-lg">
                <Shield className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-2xl mb-3">
                  Phase 8: Physiological Analysis
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  Advanced physiological inconsistency detection focusing on eye
                  movements, blink patterns, facial micro-expressions, and lip
                  synchronization. These subtle biological markers are extremely
                  difficult for AI systems to replicate accurately.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white/[0.02] border border-white/10 rounded-lg p-8 hover:border-white/20 transition-all duration-300">
            <div className="flex items-start gap-4">
              <div className="bg-white/5 p-3 rounded-lg">
                <Activity className="h-8 w-8" />
              </div>
              <div>
                <h3 className="text-2xl mb-3">
                  Phase 9: Temporal Consistency
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  Temporal consistency verification analyzes the flow and
                  coherence across frames. AI-generated videos often exhibit
                  subtle temporal discontinuities that betray their synthetic
                  nature when examined frame-by-frame.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Technology */}
        <div className="bg-white/[0.02] border border-white/10 rounded-lg p-12">
          <h2 className="text-3xl mb-6">The Technology</h2>
          <p className="text-lg text-gray-300 leading-relaxed mb-6">
            Our system combines state-of-the-art computer vision, deep learning,
            and forensic analysis techniques to provide comprehensive media
            authentication. Each detection phase is designed to catch different
            types of manipulation, creating multiple layers of verification.
          </p>
          <p className="text-gray-400 leading-relaxed">
            Sherlock.ai is built for investigators, journalists, security
            researchers, and anyone who needs to verify the authenticity of
            digital media in an age of increasingly sophisticated synthetic
            content.
          </p>
        </div>
      </div>
    </div>
  );
}
