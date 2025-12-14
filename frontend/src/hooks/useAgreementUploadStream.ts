import { useState, useCallback, useEffect } from "react";
import { uploadAgreementStream } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export interface UploadMetadata {
  session_id: string;
  document_id: string;
  expires_at: string;
  filename: string;
}

export function useAgreementUploadStream() {
  const { toast } = useToast();
  const [isUploading, setIsUploading] = useState(false);
  const [analysisText, setAnalysisText] = useState("");
  const [metadata, setMetadata] = useState<UploadMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progressStatus, setProgressStatus] = useState<string>("");

  // Restore saved analysis and metadata from localStorage on mount
  useEffect(() => {
    const savedSessionId = localStorage.getItem("session_id");
    if (savedSessionId) {
      const savedAnalysis = localStorage.getItem(`analysis_text_${savedSessionId}`);
      const savedDocumentId = localStorage.getItem("document_id");
      const savedFilename = localStorage.getItem("document_filename");
      
      if (savedAnalysis) {
        console.log("[useAgreementUploadStream] Restoring saved analysis from localStorage");
        setAnalysisText(savedAnalysis);
      }
      
      if (savedDocumentId && savedFilename) {
        setMetadata({
          session_id: savedSessionId,
          document_id: savedDocumentId,
          expires_at: "", // Not critical for display
          filename: savedFilename,
        });
      }
    }
  }, []);

  const uploadAndStream = useCallback(
    async (file: File, language: string = "en") => {
      setIsUploading(true);
      setAnalysisText("");
      setMetadata(null);
      setError(null);
      setProgressStatus("Uploading document...");

      try {
        for await (const event of uploadAgreementStream(file, language)) {
          if (event.type === "metadata") {
            setMetadata(event.data);
            // Store session_id in localStorage
            localStorage.setItem("session_id", event.data.session_id);
            localStorage.setItem("document_id", event.data.document_id);
            localStorage.setItem("document_filename", event.data.filename);
            setProgressStatus("Document uploaded. Analyzing...");
          } else if (event.type === "progress") {
            // Handle progress updates like "✓ Rights analyzed"
            setProgressStatus(event.data);
          } else if (event.type === "chunk") {
            setAnalysisText((prev) => {
              const newText = prev + event.data;
              // Persist analysis text as it streams
              const sessionId = localStorage.getItem("session_id");
              if (sessionId) {
                localStorage.setItem(`analysis_text_${sessionId}`, newText);
              }
              return newText;
            });
          } else if (event.type === "error") {
            setError(event.data);
            setProgressStatus("");
            toast({
              title: "Upload failed",
              description: event.data || "Failed to upload document",
              variant: "destructive",
            });
            break;
          }
        }

        if (!error && metadata) {
          setProgressStatus("Analysis complete!");
          toast({
            title: "Document uploaded successfully",
            description: "Your agreement has been analyzed. You can now ask questions!",
          });
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error";
        setError(errorMessage);
        setProgressStatus("");
        toast({
          title: "Upload failed",
          description: errorMessage,
          variant: "destructive",
        });
      } finally {
        setIsUploading(false);
      }
    },
    [toast, error, metadata]
  );

  const reset = useCallback(() => {
    setAnalysisText("");
    setMetadata(null);
    setError(null);
    setProgressStatus("");
    
    // Clear localStorage
    const sessionId = localStorage.getItem("session_id");
    if (sessionId) {
      localStorage.removeItem(`analysis_text_${sessionId}`);
      localStorage.removeItem(`analysis_language_${sessionId}`);
    }
    localStorage.removeItem("session_id");
    localStorage.removeItem("document_id");
    localStorage.removeItem("document_filename");
  }, []);

  return {
    uploadAndStream,
    isUploading,
    analysisText,
    metadata,
    error,
    progressStatus,
    reset,
  };
}

