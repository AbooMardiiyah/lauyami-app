import { useState, useRef, useEffect } from "react";
import { Play, Pause, Volume2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AudioPlayerProps {
  audioUrl: string;
  onEnded?: () => void;
}

export function AudioPlayer({ audioUrl, onEnded }: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handleDurationChange = () => setDuration(audio.duration);
    const handleEnded = () => {
      setIsPlaying(false);
      onEnded?.();
    };

    audio.addEventListener("timeupdate", handleTimeUpdate);
    audio.addEventListener("durationchange", handleDurationChange);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("timeupdate", handleTimeUpdate);
      audio.removeEventListener("durationchange", handleDurationChange);
      audio.removeEventListener("ended", handleEnded);
    };
  }, [onEnded]);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;
    
    const newTime = parseFloat(e.target.value);
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  return (
    <div className="flex items-center gap-3 w-full max-w-md bg-muted/50 rounded-lg p-3">
      <audio ref={audioRef} src={audioUrl} />
      
      <Button
        variant="ghost"
        size="sm"
        onClick={togglePlayPause}
        className="h-8 w-8 p-0"
      >
        {isPlaying ? (
          <Pause className="w-4 h-4" />
        ) : (
          <Play className="w-4 h-4" />
        )}
      </Button>

      <div className="flex-1">
        <input
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-1 bg-muted-foreground/20 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
        />
      </div>

      <div className="flex items-center gap-2 text-xs text-muted-foreground min-w-[80px]">
        <Volume2 className="w-3 h-3" />
        <span>
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>
      </div>
    </div>
  );
}

interface TTSButtonProps {
  text: string;
  language?: string;
  onStart?: () => void;
  onComplete?: () => void;
  onError?: (error: Error) => void;
}

export function TTSButton({
  text,
  language = "en",
  onStart,
  onComplete,
  onError,
}: TTSButtonProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const generateSpeech = async () => {
    setIsGenerating(true);
    onStart?.();

    try {
      const { textToSpeech } = await import("@/lib/api");
      console.log("[TTS] Generating speech:", { text: text.substring(0, 100), language });
      const audioBlob = await textToSpeech({ text, language });
      console.log("[TTS] Audio generated successfully, size:", audioBlob.size);
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);
    } catch (error) {
      console.error("[TTS] Error details:", error);
      onError?.(error as Error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAudioEnded = () => {
    onComplete?.();
    // Clean up URL
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  if (audioUrl) {
    return <AudioPlayer audioUrl={audioUrl} onEnded={handleAudioEnded} />;
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={generateSpeech}
      disabled={isGenerating || !text}
      className="gap-2"
    >
      {isGenerating ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin" />
          Generating...
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

