import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import {
  Upload,
  FileText,
  Mic,
  Send,
  AlertTriangle,
  CheckCircle,
  Loader2,
  Sparkles,
  Trash2,
  ArrowLeft,
  MessageCircle,
  Download,
  Volume2,
  ChevronDown,
} from "lucide-react";
import { useAgreementUploadStream } from "@/hooks/useAgreementUploadStream";
import { useChat } from "@/hooks/useChat";
// import { useVoiceQuery } from "@/hooks/useVoiceQuery"; // COMMENTED OUT - using streaming now
import { deleteSession, askWithVoiceStream, VoiceAskRequest, generateReport, textToSpeech } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { TTSButton } from "@/components/AudioPlayer";
import { LanguageSelector, SUPPORTED_LANGUAGES } from "@/components/LanguageSelector";
import { generatePDFReport } from "@/lib/pdfGenerator";
import { ListenButton } from "@/components/ListenButton";
import { DownloadReportButton } from "@/components/DownloadReportButton";
import { AnalysisDisplay } from "@/components/AnalysisDisplay";

const AppPage = () => {
  const { toast } = useToast();
  // Removed "upload" view - start directly in chat mode
  const [activeView, setActiveView] = useState<"analysis" | "chat">("chat");
  const [enableStreaming, setEnableStreaming] = useState(true);
  const [queryInput, setQueryInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(
    localStorage.getItem("session_id")
  );
  const [documentFilename, setDocumentFilename] = useState<string | null>(
    localStorage.getItem("document_filename")
  );
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedTTSLanguage, setSelectedTTSLanguage] = useState("en"); // For TTS playback
  const [analysisLanguage, setAnalysisLanguage] = useState(() => {
    // Restore saved language or default to English
    const sessionId = localStorage.getItem("session_id");
    if (sessionId) {
      return localStorage.getItem(`analysis_language_${sessionId}`) || "en";
    }
    return "en";
  }); // Language for analysis generation
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    uploadAndStream,
    isUploading,
    analysisText,
    metadata,
    error: uploadError,
    progressStatus,
    reset: resetUpload,
  } = useAgreementUploadStream();

  const { messages, setMessages, sendMessage, addMessageWithAnswer, clearMessages, isLoading: isChatLoading } = useChat(
    enableStreaming
  );

  // const voiceQueryMutation = useVoiceQuery(); // COMMENTED OUT - using streaming now
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessingVoice, setIsProcessingVoice] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [recordedChunks, setRecordedChunks] = useState<Blob[]>([]);
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null);
  
  // Audio cache for TTS - avoid regenerating same audio
  const [audioCache, setAudioCache] = useState<Record<string, Blob>>({});

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Check if we have an existing session
  useEffect(() => {
    const storedSessionId = localStorage.getItem("session_id");
    const storedFilename = localStorage.getItem("document_filename");
    
    if (storedSessionId) {
      setSessionId(storedSessionId);
      setDocumentFilename(storedFilename);
      // Stay in chat mode - no need to switch views
    }
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    resetUpload();
    setShowUploadModal(false); // Close modal
    setActiveView("analysis"); // Switch to analysis view

    // Persist selected language
    const sessionIdToUse = localStorage.getItem("session_id") || `session_${Date.now()}`;
    localStorage.setItem(`analysis_language_${sessionIdToUse}`, analysisLanguage);

    await uploadAndStream(file, analysisLanguage); // Pass selected language
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  // When upload completes with metadata, update session info
  useEffect(() => {
    if (metadata && !isUploading) {
      setSessionId(metadata.session_id);
      setDocumentFilename(metadata.filename);
      // Keep user on analysis view so they can read the results
      // They can manually switch to chat when ready using the button
    }
  }, [metadata, isUploading]);

  const handleSendMessage = async () => {
    // If recording, stop recording and send voice query
    if (isRecording) {
      await stopRecordingAndSend();
      return;
    }

    // Otherwise send text message
    if (!queryInput.trim() || isChatLoading) return;

    const query = queryInput.trim();
    setQueryInput("");
    await sendMessage(query, sessionId, analysisLanguage || "en", "natlas");
  };

  const startRecording = async () => {
    // Remove session check - allow voice without document
    // if (!sessionId) {
    //   toast({
    //     title: "No session",
    //     description: "Please upload a document first before asking questions.",
    //     variant: "destructive",
    //   });
    //   return;
    // }

    try {
      // Check if browser supports getUserMedia
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        toast({
          title: "Browser not supported",
          description: "Your browser doesn't support voice recording. Please use a modern browser like Chrome, Firefox, or Edge.",
          variant: "destructive",
        });
        return;
      }

      // Check if we're on HTTPS (required for getUserMedia in most browsers)
      if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        toast({
          title: "HTTPS required",
          description: "Voice recording requires a secure connection (HTTPS). Please use HTTPS or localhost.",
          variant: "destructive",
        });
        return;
      }

      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Create MediaRecorder
      const recorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      });
      
      const chunks: Blob[] = [];
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
          setRecordedChunks([...chunks]);
        }
      };
      
      recorder.onerror = (event) => {
        console.error("MediaRecorder error:", event);
        toast({
          title: "Recording error",
          description: "An error occurred while recording. Please try again.",
          variant: "destructive",
        });
        setIsRecording(false);
        stream.getTracks().forEach((track) => track.stop());
        setRecordedChunks([]);
      };
      
      setMediaRecorder(recorder);
      setAudioStream(stream);
      setRecordedChunks([]);
      setIsRecording(true);
      recorder.start();
      
      toast({
        title: "Recording started",
        description: "Speak your question. Click send when done.",
      });
    } catch (error) {
      console.error("Error accessing microphone:", error);
      
      let errorMessage = "Please allow microphone access to use voice queries.";
      let errorTitle = "Microphone access denied";
      
      if (error instanceof Error) {
        if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {
          errorTitle = "Microphone permission denied";
          errorMessage = "Please click the microphone icon in your browser's address bar and allow microphone access, then try again.";
        } else if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {
          errorTitle = "No microphone found";
          errorMessage = "No microphone device was found. Please connect a microphone and try again.";
        } else if (error.name === "NotReadableError" || error.name === "TrackStartError") {
          errorTitle = "Microphone in use";
          errorMessage = "Your microphone is being used by another application. Please close other apps using the microphone and try again.";
        } else if (error.name === "OverconstrainedError") {
          errorTitle = "Microphone not supported";
          errorMessage = "Your microphone doesn't support the required audio format. Please try a different microphone.";
        } else {
          errorMessage = `Error: ${error.message}. Please check your browser settings and try again.`;
        }
      }
      
      toast({
        title: errorTitle,
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const stopRecordingAndSend = async () => {
    if (!isRecording || !mediaRecorder) {
      // If not recording, just send the text message normally
      if (queryInput.trim()) {
        const query = queryInput.trim();
        setQueryInput("");
        await sendMessage(query, sessionId, analysisLanguage || "en", "natlas");
      }
      return;
    }

    // Collect all chunks before stopping
    const allChunks: Blob[] = [];
    
    // Override the existing ondataavailable to collect chunks
    const originalOndataavailable = mediaRecorder.ondataavailable;
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        allChunks.push(event.data);
      }
      // Also call original handler if it exists
      if (originalOndataavailable) {
        originalOndataavailable(event);
      }
    };

    // Set up the stop handler
    mediaRecorder.onstop = async () => {
      // Stop all tracks to release microphone
      if (audioStream) {
        audioStream.getTracks().forEach((track) => track.stop());
        setAudioStream(null);
      }
      
      // Use collected chunks or fallback to recordedChunks state
      const finalChunks = allChunks.length > 0 ? allChunks : recordedChunks;
      
      if (finalChunks.length === 0) {
        toast({
          title: "Recording failed",
          description: "No audio data was recorded. Please try again.",
          variant: "destructive",
        });
        setIsRecording(false);
        setRecordedChunks([]);
        return;
      }
      
      // Create audio file from chunks
      const audioBlob = new Blob(finalChunks, { type: "audio/webm;codecs=opus" });
      const audioFile = new File([audioBlob], "voice-query.webm", {
        type: "audio/webm;codecs=opus",
      });
      
      setIsRecording(false);
      setRecordedChunks([]);
      setIsProcessingVoice(true);
      
      // Stream voice query response
      try {
        const request: VoiceAskRequest = {
          session_id: sessionId,
          language: analysisLanguage || "en", // Use selected language from language selector
          limit: 5,
          provider: "natlas",
        };

        let transcribedText = "";
        let languageDetected = "en";
        let accumulatedAnswer = "";
        let userMessageId: string | null = null;
        let assistantMessageId: string | null = null;

        // Stream the voice response
        for await (const event of askWithVoiceStream(audioFile, request)) {
          if (event.type === "metadata") {
            // First, we get the metadata with transcribed text
            transcribedText = event.data.transcribed_text;
            languageDetected = event.data.language_detected || "en";

            // Add user message with transcribed text
            userMessageId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
            const userMessage = {
              id: userMessageId,
              role: "user" as const,
              content: transcribedText,
              language: languageDetected,
            };
            setMessages((prev: any) => [...prev, userMessage]);

            // Add loading assistant message
            assistantMessageId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
            const assistantMessage = {
              id: assistantMessageId,
              role: "assistant" as const,
              content: "",
              isLoading: true,
            };
            setMessages((prev: any) => [...prev, assistantMessage]);
          } else if (event.type === "chunk") {
            // Stream answer chunks
            accumulatedAnswer += event.data;
            if (assistantMessageId) {
              setMessages((prev: any) =>
                prev.map((msg: any) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: accumulatedAnswer, isLoading: true }
                    : msg
                )
              );
            }
          } else if (event.type === "error") {
            throw new Error(event.data);
          }
        }

        // Mark assistant message as complete
        if (assistantMessageId) {
          setMessages((prev: any) =>
            prev.map((msg: any) =>
              msg.id === assistantMessageId
                ? { ...msg, isLoading: false }
                : msg
            )
          );
        }

        setIsProcessingVoice(false);
      } catch (error) {
        setIsProcessingVoice(false);
        console.error("Voice query error:", error);
    toast({
          title: "Voice query failed",
          description: error instanceof Error ? error.message : "Failed to process voice query",
          variant: "destructive",
        });
      }
    };

    // Stop recording - this will trigger onstop
    if (mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    } else {
      setIsRecording(false);
    }
  };

  const handleDeleteSession = async () => {
    if (!sessionId) {
      // Just clear local state
      handleNewChat();
      return;
    }

    try {
      await deleteSession(sessionId);
      handleNewChat();
      toast({
        title: "Session deleted",
        description: "Your chat session has been cleared successfully.",
      });
    } catch (error) {
      console.error("Failed to delete session:", error);
      toast({
        title: "Delete failed",
        description: "Failed to delete session. Clearing locally.",
        variant: "destructive",
      });
      handleNewChat();
    }
  };
  
  // Download PDF report with optional audio (with caching)
  const handleDownloadReport = async (format: "pdf", includeAudio: boolean = false, audioLanguage: string = "en") => {
    if (!analysisText || !documentFilename) {
      toast({
        title: "Cannot generate report",
        description: "No analysis available to generate report",
        variant: "destructive",
      });
      return;
    }

    try {
      toast({
        title: "Generating PDF report...",
        description: "Creating your beautifully formatted report",
      });

      // Generate PDF using the dedicated PDF generator (without session ID)
      const pdfBlob = await generatePDFReport(analysisText, documentFilename);

      // Download PDF file
      const pdfUrl = URL.createObjectURL(pdfBlob);
      const pdfLink = document.createElement("a");
      pdfLink.href = pdfUrl;
      const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
      pdfLink.download = `lauyami_report_${timestamp}.pdf`;
      document.body.appendChild(pdfLink);
      pdfLink.click();
      document.body.removeChild(pdfLink);
      URL.revokeObjectURL(pdfUrl);

      // Optionally download audio with caching
      if (includeAudio) {
        const cacheKey = `${audioLanguage}_analysis`;
        let audioBlob: Blob;

        // Check if we already have this audio cached
        if (audioCache[cacheKey]) {
          console.log(`Using cached audio for ${audioLanguage}`);
          audioBlob = audioCache[cacheKey];
          toast({
            title: "Using cached audio",
            description: `Audio in ${SUPPORTED_LANGUAGES.find(l => l.code === audioLanguage)?.nativeName} already generated`,
          });
        } else {
          toast({
            title: "Generating audio...",
            description: `Creating audio in ${SUPPORTED_LANGUAGES.find(l => l.code === audioLanguage)?.nativeName}`,
          });

          audioBlob = await textToSpeech({
            text: analysisText,
            language: audioLanguage,
            response_format: "mp3",
          });

          // Cache the audio for future use
          setAudioCache(prev => ({ ...prev, [cacheKey]: audioBlob }));
        }

        const audioUrl = URL.createObjectURL(audioBlob);
        const audioLink = document.createElement("a");
        audioLink.href = audioUrl;
        const langName = SUPPORTED_LANGUAGES.find(l => l.code === audioLanguage)?.nativeName || audioLanguage;
        audioLink.download = `lauyami_report_${sessionId}_${langName}.mp3`;
        document.body.appendChild(audioLink);
        audioLink.click();
        document.body.removeChild(audioLink);
        URL.revokeObjectURL(audioUrl);
      }

      toast({
        title: "Report ready!",
        description: includeAudio ? "PDF and audio downloaded successfully" : "PDF downloaded successfully",
      });
    } catch (error) {
      console.error("Report generation error:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate report",
        variant: "destructive",
      });
    }
  };

  const handleNewChat = () => {
    // Clear all session data
    localStorage.removeItem("session_id");
    localStorage.removeItem("document_id");
    localStorage.removeItem("document_filename");
    setSessionId(null);
    setDocumentFilename(null);
    clearMessages();
    resetUpload();
    setActiveView("chat");
    
    toast({
      title: "New chat started",
      description: "You can now ask general questions or upload a document.",
    });
  };

  const formatAnalysisText = (text: string): JSX.Element | JSX.Element[] => {
    // Split by lines and format structured content
    const lines = text.split('\n').filter(line => line.trim());
    const elements: JSX.Element[] = [];
    let currentSection: string[] = [];
    let sectionType: 'intro' | 'right' | 'warning' | 'predatory' | 'text' = 'text';

    lines.forEach((line) => {
      const trimmed = line.trim();
      
      // Detect section types - be more flexible with matching
      if (trimmed.toLowerCase().includes('based on your tenancy agreement')) {
        if (currentSection.length > 0) {
          elements.push(renderSection(currentSection, sectionType, elements.length));
          currentSection = [];
        }
        // Extract just the sentence, remove markdown
        const cleanText = trimmed.replace(/\*\*/g, '').replace(/^.*?Based on your tenancy agreement/i, 'Based on your tenancy agreement');
        currentSection.push(cleanText);
        sectionType = 'intro';
      } else if ((trimmed.includes('✅') || trimmed.toLowerCase().includes('your right')) && trimmed.toLowerCase().includes('your right')) {
        if (currentSection.length > 0) {
          elements.push(renderSection(currentSection, sectionType, elements.length));
          currentSection = [];
        }
        // Extract text after "Your Right:"
        const match = trimmed.match(/(?:✅\s*)?\*\*?Your Right:\*\*?\s*(.+)/i);
        const content = match ? match[1].replace(/\*\*/g, '').trim() : trimmed.replace(/✅|\*\*?Your Right:\*\*?/gi, '').trim();
        currentSection.push(content);
        sectionType = 'right';
      } else if ((trimmed.includes('⚠️') || trimmed.toLowerCase().includes('warning found')) && trimmed.toLowerCase().includes('warning')) {
        if (currentSection.length > 0) {
          elements.push(renderSection(currentSection, sectionType, elements.length));
          currentSection = [];
        }
        // Extract text after "Warning Found:"
        const match = trimmed.match(/(?:⚠️\s*)?\*\*?Warning Found:\*\*?\s*(.+)/i);
        const content = match ? match[1].replace(/\*\*/g, '').trim() : trimmed.replace(/⚠️|\*\*?Warning Found:\*\*?/gi, '').trim();
        currentSection.push(content);
        sectionType = 'warning';
      } else if ((trimmed.includes('🚨') || trimmed.toLowerCase().includes('predatory')) && trimmed.toLowerCase().includes('predatory')) {
        if (currentSection.length > 0) {
          elements.push(renderSection(currentSection, sectionType, elements.length));
          currentSection = [];
        }
        // Extract text after "Predatory clause detected:"
        const match = trimmed.match(/(?:🚨\s*)?\*\*?Predatory clause detected:\*\*?\s*(.+)/i);
        const content = match ? match[1].replace(/\*\*/g, '').trim() : trimmed.replace(/🚨|\*\*?Predatory clause detected:\*\*?/gi, '').trim();
        currentSection.push(content);
        sectionType = 'predatory';
      } else if (trimmed && !trimmed.match(/^[0-9]\.|^[-*]\s|^FLAGGED|^RISKS|^SUMMARY|^RECOMMENDATIONS/i)) {
        // Regular text line - only if it's not a numbered list or section header
        if (currentSection.length > 0 && sectionType !== 'text') {
          elements.push(renderSection(currentSection, sectionType, elements.length));
          currentSection = [];
        }
        if (trimmed.length > 0) {
          currentSection.push(trimmed.replace(/\*\*/g, ''));
          sectionType = 'text';
        }
      }
    });

    // Render last section
    if (currentSection.length > 0) {
      elements.push(renderSection(currentSection, sectionType, elements.length));
      }

    return elements.length > 0 ? elements : <div className="whitespace-pre-wrap text-sm text-foreground">{text}</div>;
  };

  const renderSection = (content: string[], type: string, key: number) => {
    const text = content.join(' ').replace(/\*\*/g, '').trim();
    
    if (type === 'intro') {
      return (
        <p key={key} className="text-base font-medium text-foreground mb-4 leading-relaxed">
          {text}
        </p>
      );
    } else if (type === 'right') {
      return (
        <div key={key} className="mb-4 p-4 bg-green-50 dark:bg-green-950/20 rounded-xl border border-green-200 dark:border-green-900/30">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-green-900 dark:text-green-100 text-sm mb-1">Your Right</p>
              <p className="text-sm text-green-800 dark:text-green-200 leading-relaxed">{text}</p>
            </div>
          </div>
        </div>
      );
    } else if (type === 'warning') {
      return (
        <div key={key} className="mb-4 p-4 bg-yellow-50 dark:bg-yellow-950/20 rounded-xl border border-yellow-200 dark:border-yellow-900/30">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-yellow-900 dark:text-yellow-100 text-sm mb-1">Warning Found</p>
              <p className="text-sm text-yellow-800 dark:text-yellow-200 leading-relaxed">{text}</p>
            </div>
          </div>
        </div>
      );
    } else if (type === 'predatory') {
      return (
        <div key={key} className="mb-4 p-4 bg-red-50 dark:bg-red-950/20 rounded-xl border border-red-200 dark:border-red-900/30">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900 dark:text-red-100 text-sm mb-1">Predatory Clause Detected</p>
              <p className="text-sm text-red-800 dark:text-red-200 leading-relaxed">{text}</p>
            </div>
          </div>
        </div>
      );
    } else {
      return (
        <p key={key} className="text-sm text-foreground mb-2 leading-relaxed">
          {text}
        </p>
      );
    }
  };

  return (
    <main className="min-h-screen bg-background">
      <Navbar />
      <div className="pt-16 pb-12">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-2">
                Chat with Lauya-mi
              </h1>
              <p className="text-muted-foreground">
                Ask questions about tenancy law or upload your agreement for analysis
              </p>
            </div>

            {/* Hidden file input */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileUpload}
                    className="hidden"
                  />

            {/* Analysis View - Only shown when analyzing/viewing analysis */}
            {activeView === "analysis" && (
              <div className="bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
                {/* Analysis Header */}
                <div className="gradient-hero px-6 py-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-primary-foreground/20 flex items-center justify-center">
                        <FileText className="w-5 h-5 text-primary-foreground" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-primary-foreground">
                          {documentFilename || "Tenancy Agreement"}
                        </h3>
                        <p className="text-sm text-primary-foreground/70">
                          {isUploading ? "Analysis in progress..." : "Analysis complete"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <LanguageSelector
                        selectedLanguage={analysisLanguage}
                        onLanguageChange={setAnalysisLanguage}
                        size="sm"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleDeleteSession}
                        className="text-primary-foreground/70 hover:text-primary-foreground"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete Session
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Analysis Content */}
                <div className="p-6 max-h-[600px] overflow-y-auto">
                  {isUploading ? (
                    <div className="space-y-6">
                      {/* Progress Indicator */}
                      <div className="flex flex-col items-center justify-center py-8 space-y-4">
                      <Loader2 className="w-8 h-8 animate-spin text-primary" />
                        <div className="text-center">
                          <p className="text-muted-foreground mb-2 font-medium">
                            {progressStatus || "Analyzing document..."}
                          </p>
                          <p className="text-xs text-muted-foreground/70">
                            Analysis in progress...
                          </p>
                        </div>
                      </div>
                      
                      {/* Show partial analysis as it streams */}
                      {analysisText && (
                        <div className="border-t border-border pt-6">
                          <AnalysisDisplay analysisText={analysisText} />
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {analysisText ? (
                        <>
                          <AnalysisDisplay analysisText={analysisText} />
                          
                          {/* Listen and Download Actions */}
                          <div className="flex flex-wrap items-center gap-3 mt-6 pt-6 border-t border-border">
                            <ListenButton
                              text={analysisText}
                              language={analysisLanguage}
                              audioCache={audioCache}
                              onAudioGenerated={(language, audioBlob) => {
                                const cacheKey = `${language}_analysis`;
                                setAudioCache(prev => ({ ...prev, [cacheKey]: audioBlob }));
                              }}
                              onError={(error) => {
                                toast({
                                  title: "Speech generation failed",
                                  description: error.message,
                                  variant: "destructive",
                                });
                              }}
                            />
                            <DownloadReportButton
                              onDownload={(includeAudio) => {
                                handleDownloadReport("pdf", includeAudio, analysisLanguage);
                              }}
                            />
                        </div>
                        </>
                      ) : (
                        <div className="text-center py-12 text-muted-foreground">
                          No analysis available yet
                        </div>
                      )}

                      {metadata && analysisText && (
                        <div className="mt-6 pt-6 border-t border-border">
                          <Button
                            onClick={() => setActiveView("chat")}
                            className="w-full"
                            size="lg"
                          >
                            <Sparkles className="w-4 h-4 mr-2" />
                            Ask Questions About Your Agreement
                          </Button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Chat View - Main Interface */}
            {activeView === "chat" && (
              <div className="bg-card rounded-2xl shadow-lg border border-border flex flex-col h-[700px]">
                {/* Chat Header with Mode Indicator */}
                <div className="gradient-hero px-6 py-4">
                  <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary-foreground/20 flex items-center justify-center">
                        <MessageCircle className="w-5 h-5 text-primary-foreground" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-primary-foreground">
                          Lauya-mi
                      </h3>
                      <p className="text-sm text-primary-foreground/70">
                          Your AI Legal Assistant
                      </p>
                    </div>
                  </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleNewChat}
                        className="text-primary-foreground/70 hover:text-primary-foreground hover:bg-primary-foreground/10"
                        title="Start new chat"
                      >
                        <Sparkles className="w-4 h-4 mr-2" />
                        New Chat
                      </Button>
                      {sessionId && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleDeleteSession}
                          className="text-primary-foreground/70 hover:text-primary-foreground hover:bg-primary-foreground/10"
                          title="Delete session"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                  
                  {/* Mode Indicator */}
                  <div className="flex items-center gap-2 flex-wrap">
                    {documentFilename ? (
                      <div className="flex items-center gap-2 bg-primary-foreground/20 px-3 py-1.5 rounded-full">
                        <FileText className="w-4 h-4 text-primary-foreground" />
                        <span className="text-sm text-primary-foreground font-medium">
                          Analyzing: {documentFilename}
                        </span>
                        <button
                          onClick={() => setActiveView("analysis")}
                          className="text-primary-foreground/70 hover:text-primary-foreground ml-1"
                          title="View analysis"
                        >
                          <ArrowLeft className="w-3 h-3" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 bg-primary-foreground/20 px-3 py-1.5 rounded-full">
                        <MessageCircle className="w-4 h-4 text-primary-foreground" />
                        <span className="text-sm text-primary-foreground font-medium">
                          General Chat
                        </span>
                      </div>
                    )}
                    
                    {/* Language Selector for Analysis */}
                    <LanguageSelector
                      selectedLanguage={analysisLanguage}
                      onLanguageChange={setAnalysisLanguage}
                      size="sm"
                    />
                    
                    {/* Upload Document Button */}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleUploadClick}
                      disabled={isUploading}
                      className="bg-primary-foreground/10 hover:bg-primary-foreground/20 text-primary-foreground px-3 py-1.5 h-auto"
                    >
                      {isUploading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          Upload Document
                        </>
                      )}
                    </Button>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  {messages.length === 0 && !isUploading && (
                    <div className="text-center py-12 text-muted-foreground">
                      <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p className="text-lg mb-2">Ask me anything about Lagos State tenancy law</p>
                      <p className="text-sm mt-2">
                        Try: "What are my rights as a tenant?" or upload your agreement for specific analysis
                      </p>
                    </div>
                  )}

                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-2xl px-5 py-4 ${
                          msg.role === "user"
                            ? "bg-primary/10 rounded-br-md"
                            : "bg-muted rounded-bl-md"
                        }`}
                      >
                        {msg.role === "assistant" && msg.isLoading && (
                          <div className="flex items-center gap-2 mb-2">
                            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
                            <span className="text-xs text-muted-foreground">Thinking...</span>
                          </div>
                        )}
                        {msg.role === "user" && msg.language && (
                          <p className="text-xs text-muted-foreground mb-2">
                            {msg.language} • Voice
                          </p>
                        )}
                        <div className="text-foreground text-sm leading-relaxed prose prose-sm max-w-none dark:prose-invert prose-headings:font-semibold prose-p:mb-2 prose-p:mt-0 prose-ul:my-2 prose-ol:my-2 prose-li:my-1 prose-strong:font-semibold prose-strong:text-foreground prose-code:text-sm prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:rounded">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                        
                        {/* TTS Button for assistant messages */}
                        {msg.role === "assistant" && msg.content && !msg.isLoading && (
                          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border/50">
                            <ListenButton
                              text={msg.content}
                              language="en"
                              audioCache={audioCache}
                              cacheKey={`chat_${msg.id}`}
                              onAudioGenerated={(cacheKey, audioBlob) => {
                                setAudioCache(prev => ({ ...prev, [cacheKey]: audioBlob }));
                              }}
                              onError={(error) => {
                                toast({
                                  title: "Speech generation failed",
                                  description: error.message,
                                  variant: "destructive",
                                });
                              }}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-border">
                  <div className="flex items-center gap-3 bg-muted rounded-xl px-4 py-3">
                    <input
                      type="text"
                      value={queryInput}
                      onChange={(e) => setQueryInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder="Ask about tenancy law..."
                      className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
                      disabled={isChatLoading}
                    />
                    <button
                      onClick={startRecording}
                      disabled={isChatLoading || isProcessingVoice || isRecording}
                      className={`w-10 h-10 rounded-full flex items-center justify-center hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed relative ${
                        isRecording
                          ? "bg-destructive animate-pulse"
                          : "gradient-warm"
                      }`}
                      title={isRecording ? "Recording in progress..." : isProcessingVoice ? "Processing voice query..." : "Click to start voice recording"}
                    >
                      {isRecording ? (
                        <>
                          <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
                          <div className="absolute inset-0 rounded-full border-2 border-white animate-ping opacity-75" />
                        </>
                      ) : isProcessingVoice ? (
                        <Loader2 className="w-5 h-5 text-secondary-foreground animate-spin" />
                      ) : (
                      <Mic className="w-5 h-5 text-secondary-foreground" />
                      )}
                    </button>
                    <button
                      onClick={handleSendMessage}
                      disabled={isChatLoading || (!queryInput.trim() && !isRecording)}
                      className="w-10 h-10 rounded-full gradient-hero flex items-center justify-center hover:scale-105 transition-transform disabled:opacity-50 disabled:cursor-not-allowed"
                      title={isRecording ? "Click to stop recording and send" : "Send message"}
                    >
                      {isChatLoading || isProcessingVoice ? (
                        <Loader2 className="w-5 h-5 text-primary-foreground animate-spin" />
                      ) : (
                        <Send className="w-5 h-5 text-primary-foreground" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      <Footer />
    </main>
  );
};

export default AppPage;

