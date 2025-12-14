import { useState } from "react";
import { Volume2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { textToSpeech } from "@/lib/api";

interface ListenButtonProps {
  text: string;
  language: string; // Language to use (from analysis)
  onError?: (error: Error) => void;
  audioCache?: Record<string, Blob>;
  onAudioGenerated?: (language: string, audioBlob: Blob) => void;
}

export function ListenButton({ text, language, onError, audioCache = {}, onAudioGenerated }: ListenButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const handleGenerateSpeech = async () => {
    setIsGenerating(true);

    try {
      const cacheKey = `${language}_analysis`;
      let audioBlob: Blob;

      // Check cache first
      if (audioCache[cacheKey]) {
        console.log(`[Listen] Using cached audio for ${language}`);
        audioBlob = audioCache[cacheKey];
      } else {
        console.log(`[Listen] Generating new audio for ${language}`);
        audioBlob = await textToSpeech({ text, language });
        
        // Notify parent to cache this audio
        onAudioGenerated?.(language, audioBlob);
      }

      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
      
      // Auto-play
      const audio = new Audio(url);
      audio.play();
      setIsPlaying(true);
      
      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(url);
        setAudioUrl(null);
      };
    } catch (error) {
      console.error("[Listen] TTS error:", error);
      onError?.(error as Error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleGenerateSpeech}
      disabled={isGenerating || isPlaying || !text}
      className="gap-2"
    >
      {isGenerating || isPlaying ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          {isGenerating ? "Generating..." : "Playing..."}
        </>
      ) : (
        <>
          <Volume2 className="w-4 h-4" />
          Listen
        </>
      )}
    </Button>
  );
}
