import { useState, useRef } from "react";
import { detectVideo, validateFile } from "@/api/sherlockApi";
import type { VideoDetectionResult } from "@/api/sherlockApi";
import { Button } from "./ui/button";
import { Upload, Check, X, Eye, Mic2, Loader2, AlertCircle } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

export function VideoDetection() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VideoDetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    // Validate file
    const validation = validateFile(file, "video");
    if (!validation.valid) {
      setError(validation.error || "Invalid file");
      return;
    }

    setSelectedFile(file);
    setResult(null);
    setError(null);

    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const analyzeVideo = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const data = await detectVideo(selectedFile);
      setResult(data);
    } catch (err) {
      console.error("Video detection failed:", err);
      setError(err instanceof Error ? err.message : "Detection failed");
    } finally {
      setLoading(false);
    }
  };

  const trustGraph =
    result?.frames.slice(0, 100).map((f) => ({
      frame: f.frame_id,
      phase8: f.phase8_trust * 100,
      phase9: f.phase9_trust * 100,
    })) ?? [];

  const verdictColor = {
    REAL: "text-green-400",
    FAKE: "text-red-400",
    UNKNOWN: "text-yellow-400",
  };

  return (
    <div className="min-h-screen pt-32 pb-20 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl mb-6 tracking-tight font-light">Video Detection</h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Multi-phase deepfake detection with temporal trust fusion and frame-by-frame analysis
          </p>
        </div>

        {/* Upload */}
        <div className="mb-12">
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-white/10 rounded-lg p-12 text-center cursor-pointer bg-white/[0.02] hover:border-white/20 transition max-w-2xl mx-auto min-h-[400px] flex flex-col items-center justify-center"
          >
            {preview ? (
              <>
                <video
                  src={preview}
                  controls
                  className="max-h-96 mx-auto rounded-lg mb-4"
                />
                <p className="text-sm text-gray-400">{selectedFile?.name}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {((selectedFile?.size || 0) / 1024 / 1024).toFixed(2)} MB
                </p>
              </>
            ) : (
              <>
                <Upload className="h-16 w-16 mx-auto text-gray-600 mb-4" />
                <p className="text-lg mb-2">Drop video here or click to browse</p>
                <p className="text-sm text-gray-400">
                  Supported: MP4, WebM, AVI, MOV (max 100MB)
                </p>
              </>
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="video/mp4,video/webm,video/avi,video/quicktime"
            onChange={handleFileInput}
            className="hidden"
          />

          {error && (
            <div className="max-w-2xl mx-auto mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          <Button
            onClick={analyzeVideo}
            disabled={!selectedFile || loading}
            className="w-full max-w-2xl mx-auto mt-6 bg-white text-black hover:bg-gray-200 py-6 text-lg block"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin inline" />
                Analyzing video...
              </>
            ) : (
              "Analyze Video"
            )}
          </Button>
        </div>

        {/* Loading */}
        {loading && (
          <div className="bg-white/[0.02] border border-white/10 rounded-lg p-12 text-center">
            <Loader2 className="w-12 h-12 mx-auto mb-4 animate-spin text-gray-400" />
            <p className="text-lg mb-2">Processing video frames...</p>
            <p className="text-sm text-gray-400">
              This may take a minute depending on video length
            </p>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-8">
            {/* Phase Verdicts */}
            <div className="grid md:grid-cols-3 gap-6">
              {[
                { label: "Phase 7", verdict: result.phase7_verdict, description: "Multi-model voting" },
                { label: "Phase 8", verdict: result.phase8_verdict, description: "Face/Eye/Lip analysis" },
                { label: "Phase 9", verdict: result.phase9_verdict, description: "Temporal fusion" },
              ].map(({ label, verdict, description }) => (
                <div
                  key={label}
                  className="bg-white/[0.02] border border-white/10 rounded-lg p-6"
                >
                  <h3 className="text-sm text-gray-400 mb-1">{label}</h3>
                  <p className="text-xs text-gray-500 mb-3">{description}</p>
                  <div className="flex items-center gap-2">
                    {verdict === "REAL" ? (
                      <Check className="w-5 h-5 text-green-400" />
                    ) : verdict === "FAKE" ? (
                      <X className="w-5 h-5 text-red-400" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-yellow-400" />
                    )}
                    <span className={`text-xl font-medium ${verdictColor[verdict]}`}>
                      {verdict}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Trust Scores */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white/[0.02] border border-white/10 rounded-lg p-6">
                <h3 className="text-sm text-gray-400 mb-3">Phase 8 Trust Score</h3>
                <p className="text-3xl font-light">
                  {(result.phase8_trust_score * 100).toFixed(1)}%
                </p>
              </div>
              <div className="bg-white/[0.02] border border-white/10 rounded-lg p-6">
                <h3 className="text-sm text-gray-400 mb-3">Phase 9 Trust Score</h3>
                <p className="text-3xl font-light">
                  {(result.phase9_trust_score * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Trust Graph */}
            <div className="bg-white/[0.02] border border-white/10 rounded-lg p-8">
              <h3 className="text-xl mb-6 font-light">Temporal Trust Fusion</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trustGraph}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis
                    dataKey="frame"
                    stroke="#666"
                    label={{ value: "Frame", position: "insideBottom", offset: -5 }}
                  />
                  <YAxis
                    stroke="#666"
                    label={{ value: "Trust %", angle: -90, position: "insideLeft" }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1a1a1a",
                      border: "1px solid #333",
                      borderRadius: "8px",
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="phase8"
                    stroke="#4d90fe"
                    dot={false}
                    name="Phase 8"
                    strokeWidth={2}
                  />
                  <Line
                    type="monotone"
                    dataKey="phase9"
                    stroke="#34a853"
                    dot={false}
                    name="Phase 9"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Statistics */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-white/[0.02] border border-white/10 rounded-lg p-6">
                <h3 className="text-sm text-gray-400 mb-3">Phase 7 Distribution</h3>
                <div className="space-y-2 text-sm">
                  {Object.entries(result.phase7_distribution).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className={verdictColor[key as keyof typeof verdictColor] || "text-gray-400"}>
                        {key}
                      </span>
                      <span>{value} frames</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white/[0.02] border border-white/10 rounded-lg p-6">
                <h3 className="text-sm text-gray-400 mb-3">Eye Analysis</h3>
                <div className="space-y-2 text-sm">
                  {Object.entries(result.phase8_eyes_distribution).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span>{key}</span>
                      <span>{value} frames</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white/[0.02] border border-white/10 rounded-lg p-6">
                <h3 className="text-sm text-gray-400 mb-3">Lip Sync Analysis</h3>
                <div className="space-y-2 text-sm">
                  {Object.entries(result.phase8_lips_distribution).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span>{key}</span>
                      <span>{value} frames</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Frame Table */}
            <div className="bg-white/[0.02] border border-white/10 rounded-lg p-8 overflow-x-auto">
              <h3 className="text-xl mb-6 font-light">
                Frame-by-Frame Analysis (first 20 frames)
              </h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10 text-left">
                    <th className="pb-3 px-4">Frame</th>
                    <th className="pb-3 px-4">Verdict</th>
                    <th className="pb-3 px-4">P8 Trust</th>
                    <th className="pb-3 px-4">P9 Trust</th>
                    <th className="pb-3 px-4">Eyes</th>
                    <th className="pb-3 px-4">Lips</th>
                  </tr>
                </thead>
                <tbody>
                  {result.frames.slice(0, 20).map((f) => (
                    <tr key={f.frame_id} className="border-b border-white/5 hover:bg-white/[0.02]">
                      <td className="py-3 px-4">{f.frame_id}</td>
                      <td
                        className={`py-3 px-4 font-medium ${verdictColor[f.verdict]}`}
                      >
                        {f.verdict}
                      </td>
                      <td className="py-3 px-4">{(f.phase8_trust * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4">{(f.phase9_trust * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4">
                        <Eye className="inline h-4 w-4 mr-1" />
                        {f.eye_verdict}
                      </td>
                      <td className="py-3 px-4">
                        <Mic2 className="inline h-4 w-4 mr-1" />
                        {f.lip_verdict}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="text-xs text-gray-500 mt-4">
                Showing 20 of {result.total_frames} analyzed frames
              </p>
            </div>
          </div>
        )}

        {!loading && !result && (
          <div className="bg-white/[0.02] border border-white/10 rounded-lg p-12 text-center text-gray-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>Upload a video to begin forensic analysis</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoDetection;
