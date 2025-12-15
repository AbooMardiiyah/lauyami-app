/**
 * API service layer for backend communication
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Debug: Log the API base URL being used
if (import.meta.env.DEV) {
  console.log("[API] API_BASE_URL:", API_BASE_URL);
  console.log("[API] VITE_API_BASE_URL env:", import.meta.env.VITE_API_BASE_URL);
}

export interface UploadAgreementResponse {
  session_id: string;
  document_id: string;
  extracted_text: string;
  analysis: string;
  flagged_clauses: string[];
  risks: string[];
  summary: string;
  recommendations: string;
  sources: string[];
  language: string;
  expires_at: string;
}

export interface AskRequest {
  query_text: string;
  session_id?: string | null;
  feed_author?: string | null;
  feed_name?: string | null;
  article_author?: string[] | null;
  title_keywords?: string | null;
  limit?: number;
  provider?: string;
  model?: string | null;
  language?: string;
}

export interface AskResponse {
  query: string;
  provider: string;
  answer: string;
  sources: Array<{
    title: string;
    feed_author?: string;
    feed_name?: string;
    article_author?: string[];
    url?: string;
    chunk_text?: string;
    score: number;
  }>;
  model?: string | null;
  finish_reason?: string | null;
}

export interface VoiceAskRequest {
  session_id?: string | null;
  language?: string;
  limit?: number;
  provider?: string;
}

export interface VoiceAskResponse {
  transcribed_text: string;
  language_detected: string;
  query: string;
  answer: string;
  sources: Array<{
    title: string;
    feed_author?: string;
    feed_name?: string;
    article_author?: string[];
    url?: string;
    chunk_text?: string;
    score: number;
  }>;
  model?: string | null;
}

export async function* askQuestionStream(
  request: AskRequest
): AsyncGenerator<string, void, unknown> {
  const response = await fetch(`${API_BASE_URL}/search/ask/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query_text: request.query_text,
      session_id: request.session_id,
      feed_author: request.feed_author || null,
      feed_name: request.feed_name || null,
      article_author: request.article_author || null,
      title_keywords: request.title_keywords || null,
      limit: request.limit || 5,
      provider: request.provider || "natlas",
      model: request.model || null,
      language: request.language || "en",
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Streaming query failed: ${error}`);
  }

  if (!response.body) {
    throw new Error("No response body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  try {
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      yield chunk;
    }
  } finally {
    reader.releaseLock();
  }
}

export async function* askWithVoiceStream(
  audioFile: File,
  request: VoiceAskRequest
): AsyncGenerator<
  | { type: "metadata"; data: { transcribed_text: string; language_detected: string; query: string; num_sources: number } }
  | { type: "chunk"; data: string }
  | { type: "error"; data: string },
  void,
  unknown
> {
  const formData = new FormData();
  formData.append("audio_file", audioFile);
  formData.append("language", request.language || "en");
  formData.append("limit", String(request.limit || 5));
  formData.append("provider", request.provider || "natlas");
  
  if (request.session_id) {
    formData.append("session_id", request.session_id);
  }

  const response = await fetch(`${API_BASE_URL}/voice/ask-with-voice`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.text();
    yield { type: "error", data: `Voice query failed: ${error}` };
    return;
  }

  if (!response.body) {
    yield { type: "error", data: "No response body" };
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("__metadata__:")) {
          try {
            const metadata = JSON.parse(line.replace("__metadata__:", ""));
            yield { type: "metadata", data: metadata };
          } catch (e) {
            // Invalid metadata, continue
          }
        } else if (line.startsWith("__progress__:")) {
          // Handle progress updates
          const progress = line.replace("__progress__:", "").trim();
          yield { type: "progress", data: progress };
        } else if (line.startsWith("__error__:")) {
          yield { type: "error", data: line.replace("__error__:", "") };
          return;
        } else if (line.trim()) {
          yield { type: "chunk", data: line };
        }
      }
    }

    // Process remaining buffer
    if (buffer.trim()) {
      if (buffer.startsWith("__metadata__:")) {
        try {
          const metadata = JSON.parse(buffer.replace("__metadata__:", ""));
          yield { type: "metadata", data: metadata };
        } catch (e) {
          // Invalid metadata
        }
      } else if (!buffer.startsWith("__error__:")) {
        yield { type: "chunk", data: buffer };
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Upload agreement and stream analysis
 */
export async function* uploadAgreementStream(
  file: File,
  language: string = "en"
): AsyncGenerator<
  | { type: "metadata"; data: { session_id: string; document_id: string; expires_at: string; filename: string } }
  | { type: "chunk"; data: string }
  | { type: "error"; data: string },
  void,
  unknown
> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("language", language);

  let response: Response;
  try {
    const uploadUrl = `${API_BASE_URL}/agreement/upload-agreement/stream`;
    console.log(`[Upload] Attempting to upload to: ${uploadUrl}`);
    response = await fetch(uploadUrl, {
      method: "POST",
      body: formData,
      // Don't set timeout here - let the browser handle it, but we'll catch errors
    });
    console.log(`[Upload] Response status: ${response.status} ${response.statusText}`);
  } catch (fetchError) {
    // Handle network errors (connection refused, timeout, etc.)
    const errorMessage = fetchError instanceof Error 
      ? fetchError.message 
      : "Network error: Failed to connect to backend server";
    yield { type: "error", data: `Failed to fetch: ${errorMessage}. Please check if the backend server is running at ${API_BASE_URL}` };
    return;
  }

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const contentType = response.headers.get("content-type");
      if (contentType?.includes("application/json")) {
        // Backend returned JSON error (from exception handlers)
        const errorJson = await response.json();
        errorMessage = errorJson.message || errorJson.details || JSON.stringify(errorJson);
        console.error("[Upload] Backend JSON error:", errorJson);
      } else {
        // Backend returned text error
        const errorText = await response.text();
        errorMessage = errorText || errorMessage;
        console.error("[Upload] Backend text error:", errorText);
      }
    } catch (e) {
      // If we can't read the error, use the status
      console.error("[Upload] Failed to read error response:", e);
      errorMessage = `HTTP ${response.status}: ${response.statusText}. Check backend logs for details.`;
    }
    yield { type: "error", data: errorMessage };
    return;
  }

  if (!response.body) {
    yield { type: "error", data: "No response body" };
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("__metadata__:")) {
          try {
            const metadata = JSON.parse(line.replace("__metadata__:", ""));
            yield { type: "metadata", data: metadata };
          } catch (e) {
            // Invalid metadata, continue
          }
        } else if (line.startsWith("__progress__:")) {
          // Handle progress updates
          const progress = line.replace("__progress__:", "").trim();
          yield { type: "progress", data: progress };
        } else if (line.startsWith("__error__:")) {
          yield { type: "error", data: line.replace("__error__:", "") };
          return;
        } else if (line.trim()) {
          yield { type: "chunk", data: line };
        }
      }
    }

    // Process remaining buffer
    if (buffer.trim()) {
      if (buffer.startsWith("__metadata__:")) {
        try {
          const metadata = JSON.parse(buffer.replace("__metadata__:", ""));
          yield { type: "metadata", data: metadata };
        } catch (e) {
          // Invalid metadata
        }
      } else if (!buffer.startsWith("__error__:")) {
        yield { type: "chunk", data: buffer };
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Delete a session
 */
export async function deleteSession(sessionId: string): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/agreement/session/${sessionId}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Delete session failed: ${error}`);
  }
}

// =====================
// Text-to-Speech API
// =====================

export interface TTSRequest {
  text: string;
  language?: string;  // yo, ha, ig, en
  voice?: string;     
  response_format?: string; 
}

export interface Voice {
  voice: string;
  description: string;
}

export interface VoicesResponse {
  voices: Record<string, Voice>;
}

/**
 * Convert text to speech using YarnGPT API
 * @param request - TTS request with text and language
 * @returns Audio blob
 */
export async function textToSpeech(request: TTSRequest): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/tts/text-to-speech`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text: request.text,
      language: request.language || "en",
      voice: request.voice,
      response_format: request.response_format || "mp3",
    }),
  });

  if (!response.ok) {
    let errorMessage = "Failed to generate speech";
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {

      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return await response.blob();
}

export async function getAvailableVoices(): Promise<VoicesResponse> {
  const response = await fetch(`${API_BASE_URL}/tts/voices`);
  
  if (!response.ok) {
    throw new Error("Failed to fetch available voices");
  }
  
  return await response.json();
}

// For Report Generation

export interface GenerateReportRequest {
  analysis_text: string;
  document_filename: string;
  session_id: string;
  format: "text" | "html" | "json";
}

/**
 * Generate a summary report from analysis
 * @param request - Report generation request
 * @returns Blob of the generated report
 */
export async function generateReport(request: GenerateReportRequest): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/report/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorMessage = "Failed to generate report";
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return await response.blob();
}

