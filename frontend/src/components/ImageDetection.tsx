import { useRef, useState } from "react";
import { detectImage, validateFile } from "@/api/sherlockApi";
import type { ImageDetectionResult } from "@/api/sherlockApi";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Upload, Check, X, AlertCircle, Loader2 } from "lucide-react";

export function ImageDetection() {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImageDetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  /* ============================
     FILE SELECTION
  ============================ */
  const handleFileChange = (file: File | null) => {
    if (!file) return;

    // Validate file
    const validation = validateFile(file, "image");
    if (!validation.valid) {
      setError(validation.error || "Invalid file");
      return;
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  /* ============================
     IMAGE ANALYSIS
  ============================ */
  const analyzeImage = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await detectImage(selectedFile);
      setResult(res);
    } catch (err) {
      console.error("Image detection failed:", err);
      setError(err instanceof Error ? err.message : "Detection failed");
    } finally {
      setLoading(false);
    }
  };

  /* ============================
     UI HELPERS
  ============================ */
  const verdictIcon = {
    REAL: <Check className="w-6 h-6 text-green-500" />,
    FAKE: <X className="w-6 h-6 text-red-500" />,
    UNKNOWN: <AlertCircle className="w-6 h-6 text-yellow-500" />,
  };

  const verdictColor = {
    REAL: "text-green-400",
    FAKE: "text-red-400",
    UNKNOWN: "text-yellow-400",
  };

  /* ============================
     RENDER
  ============================ */
  return (
    <div className="min-h-screen pt-32 pb-20 px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl mb-6 tracking-tight font-light">Image Detection</h1>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Upload an image to detect if it's AI-generated using multi-model ensemble analysis
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* UPLOAD PANEL */}
          <div className="lg:col-span-2 bg-white/[0.02] border border-white/10 rounded-xl p-8">
            <div
              className="border-2 border-dashed border-white/20 rounded-lg p-12 flex flex-col items-center justify-center cursor-pointer hover:border-white/40 transition min-h-[400px]"
              onClick={() => fileInputRef.current?.click()}
            >
              {previewUrl ? (
                <div className="w-full h-full flex flex-col items-center">
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="max-h-96 rounded-lg object-contain mb-4"
                  />
                  <p className="text-sm text-gray-400">{selectedFile?.name}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {((selectedFile?.size || 0) / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <>
                  <Upload className="w-16 h-16 mb-4 text-gray-600" />
                  <p className="text-lg mb-2">Drop image here or click to browse</p>
                  <p className="text-sm text-gray-400">
                    Supported: JPEG, PNG, WebP (max 10MB)
                  </p>
                </>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              hidden
              onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
            />

            {error && (
              <div className="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <Button
              className="mt-6 w-full bg-white text-black hover:bg-gray-200 py-6 text-lg"
              disabled={!selectedFile || loading}
              onClick={analyzeImage}
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                "Analyze Image"
              )}
            </Button>
          </div>

          {/* RESULTS PANEL */}
          <div className="bg-white/[0.02] border border-white/10 rounded-xl p-8 space-y-6">
            {/* FINAL VERDICT */}
            <div>
              <h3 className="text-sm text-gray-400 mb-3">Final Verdict</h3>
              <div className="flex items-center gap-3">
                {result && verdictIcon[result.verdict]}
                <span
                  className={`text-2xl font-medium ${
                    result ? verdictColor[result.verdict] : "text-gray-500"
                  }`}
                >
                  {result?.verdict || "—"}
                </span>
              </div>
            </div>

            {/* TRUST SCORE */}
            <div>
              <h3 className="text-sm text-gray-400 mb-3">Trust Score</h3>
              <Progress
                value={result ? result.trust_score : 0}
                className="mb-2"
              />
              <p className="text-sm">
                {result ? result.trust_score.toFixed(1) : "0.0"}%
              </p>
            </div>

            {/* PROBABILITIES */}
            {result && (
              <div>
                <h3 className="text-sm text-gray-400 mb-3">Model Predictions</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-green-400">Real Probability</span>
                    <span>{(result.real_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-red-400">Fake Probability</span>
                    <span>{(result.fake_probability * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            )}

            {/* DETECTION METRICS */}
            {result && (
              <div>
                <h3 className="text-sm text-gray-400 mb-3">Detection Metrics</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Entropy</span>
                    <span>{result.entropy.toFixed(3)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">OOD Distance</span>
                    <span>{result.ood_distance.toFixed(2)}</span>
                  </div>
                  {result.phase7_score !== null && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Phase 7 Score</span>
                      <span>{(result.phase7_score * 100).toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {!result && !loading && (
              <div className="text-center text-gray-500 pt-12">
                <AlertCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Upload an image to see results</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ImageDetection;
