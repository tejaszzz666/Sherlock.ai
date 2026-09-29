/**
 * Sherlock.ai API Client
 * Type-safe API calls to the backend detection service
 */

// Configuration
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// ============ Types ============

export interface ImageDetectionResult {
  verdict: "REAL" | "FAKE" | "UNKNOWN";
  trust_score: number;
  real_probability: number;
  fake_probability: number;
  entropy: number;
  ood_distance: number;
  phase7_score: number | null;
  phase8_score: number | null;
  phase9_score: number | null;
}

export interface FrameAnalysis {
  frame_id: number;
  verdict: "REAL" | "FAKE" | "UNKNOWN";
  phase8_trust: number;
  phase9_trust: number;
  real_probability: number;
  fake_probability: number;
  eye_verdict: string;
  lip_verdict: string;
  entropy?: number;
  ood_distance?: number;
}

export interface VideoDetectionResult {
  phase7_verdict: "REAL" | "FAKE" | "UNKNOWN";
  phase8_verdict: "REAL" | "FAKE" | "UNKNOWN";
  phase9_verdict: "REAL" | "FAKE" | "UNKNOWN";
  phase8_trust_score: number;
  phase9_trust_score: number;
  total_frames: number;
  frames: FrameAnalysis[];
  phase7_distribution: Record<string, number>;
  phase8_eyes_distribution: Record<string, number>;
  phase8_lips_distribution: Record<string, number>;
}

export interface ApiError {
  error: string;
  message: string;
  detail?: string;
}

// ============ Utility Functions ============

const safeNumber = (value: any): number => {
  const n = Number(value);
  return isNaN(n) || !isFinite(n) ? 0 : n;
};

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      error: "NetworkError",
      message: `HTTP ${response.status}: ${response.statusText}`,
    }));
    throw new Error(error.message || "API request failed");
  }
  return response.json();
}

// ============ API Functions ============

/**
 * Detect if an image is real or AI-generated
 */
export async function detectImage(file: File): Promise<ImageDetectionResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/detect-image`, {
    method: "POST",
    body: formData,
  });

  const data = await handleResponse<ImageDetectionResult>(response);

  // Backend now returns proper fields
  return {
    verdict: data.verdict,
    trust_score: safeNumber(data.trust_score),
    real_probability: safeNumber(data.real_probability),
    fake_probability: safeNumber(data.fake_probability),
    entropy: safeNumber(data.entropy),
    ood_distance: safeNumber(data.ood_distance),
    phase7_score: data.phase7_score !== null ? safeNumber(data.phase7_score) : null,
    phase8_score: data.phase8_score !== null ? safeNumber(data.phase8_score) : null,
    phase9_score: data.phase9_score !== null ? safeNumber(data.phase9_score) : null,
  };
}

/**
 * Detect if a video is real or AI-generated using frame-by-frame analysis
 */
export async function detectVideo(
  file: File,
  onProgress?: (progress: number) => void
): Promise<VideoDetectionResult> {
  const formData = new FormData();
  formData.append("file", file);

  // Note: Progress tracking would require server-sent events or websockets
  // For now, we just indicate upload completion
  const response = await fetch(`${API_BASE}/detect-video`, {
    method: "POST",
    body: formData,
  });

  if (onProgress) {
    onProgress(100);
  }

  return handleResponse<VideoDetectionResult>(response);
}

/**
 * Health check - verify backend is running
 */
export async function checkHealth(): Promise<{ status: string; models_loaded: boolean }> {
  const response = await fetch(`${API_BASE}/health`);
  return handleResponse(response);
}

/**
 * Validate file before upload
 */
export function validateFile(
  file: File,
  type: "image" | "video"
): { valid: boolean; error?: string } {
  const maxSizeMB = type === "image" ? 10 : 100;
  const maxSizeBytes = maxSizeMB * 1024 * 1024;

  if (file.size > maxSizeBytes) {
    return {
      valid: false,
      error: `File too large. Maximum size: ${maxSizeMB}MB`,
    };
  }

  if (file.size === 0) {
    return {
      valid: false,
      error: "File is empty",
    };
  }

  const allowedTypes =
    type === "image"
      ? ["image/jpeg", "image/png", "image/webp"]
      : ["video/mp4", "video/webm", "video/avi", "video/quicktime"];

  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `Invalid file type. Allowed: ${allowedTypes.join(", ")}`,
    };
  }

  return { valid: true };
}
