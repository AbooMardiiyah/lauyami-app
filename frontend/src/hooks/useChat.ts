import { useState, useCallback, useRef } from "react";
import { useMutation } from "@tanstack/react-query";
// import { askQuestion, askQuestionStream, AskRequest } from "@/lib/api"; // askQuestion commented out (non-streaming)
import { askQuestionStream, AskRequest } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  language?: string;
  sources?: Array<{
    title: string;
    feed_author?: string;
    feed_name?: string;
    url?: string;
    chunk_text?: string;
    score: number;
  }>;
  isLoading?: boolean;
}

export function useChat(enableStreaming: boolean = true) {
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  const addMessage = useCallback((message: Omit<Message, "id">) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
    };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage.id;
  }, []);

  const updateMessage = useCallback((id: string, updates: Partial<Message>) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === id ? { ...msg, ...updates } : msg))
    );
  }, []);

  // NON-STREAMING MUTATION - COMMENTED OUT (streaming only now)
  // const nonStreamingMutation = useMutation({
  //   mutationFn: async (request: AskRequest) => {
  //     return askQuestion(request);
  //   },
  //   onSuccess: (response, variables) => {
  //     // Find the loading message and update it
  //     setMessages((prev) => {
  //       const updated = [...prev];
  //       const loadingIndex = updated.findIndex(
  //         (msg) => msg.role === "assistant" && msg.isLoading
  //       );
        
  //       if (loadingIndex !== -1) {
  //         updated[loadingIndex] = {
  //           ...updated[loadingIndex],
  //           content: response.answer,
  //           isLoading: false,
  //           sources: response.sources,
  //         };
  //       }
        
  //       return updated;
  //     });
  //   },
  //   onError: (error: Error) => {
  //     setMessages((prev) => {
  //       const updated = [...prev];
  //       const loadingIndex = updated.findIndex(
  //         (msg) => msg.role === "assistant" && msg.isLoading
  //       );
        
  //       if (loadingIndex !== -1) {
  //         updated[loadingIndex] = {
  //           ...updated[loadingIndex],
  //           content: `Error: ${error.message}`,
  //           isLoading: false,
  //         };
  //       }
        
  //       return updated;
  //     });
      
  //     toast({
  //       title: "Query failed",
  //       description: error.message || "Failed to get answer",
  //       variant: "destructive",
  //     });
  //   },
  // });

  const sendMessage = useCallback(
    async (
      query: string,
      sessionId?: string | null,
      language?: string,
      provider: string = "natlas"
    ) => {
      // Cancel previous request if any
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Add user message
      const userMessageId = addMessage({
        role: "user",
        content: query,
        language,
      });

      // Add loading assistant message
      const assistantMessageId = addMessage({
        role: "assistant",
        content: "",
        isLoading: true,
      });

      const request: AskRequest = {
        query_text: query,
        session_id: sessionId || localStorage.getItem("session_id") || null,
        provider,
        limit: 5,
      };

      try {
        // ALWAYS use streaming mode now (non-streaming removed)
        // if (enableStreaming) {
          // Streaming mode
          let accumulatedContent = "";

          for await (const chunk of askQuestionStream(request)) {
            // Check if request was aborted
            if (abortControllerRef.current?.signal.aborted) {
              break;
            }

            accumulatedContent += chunk;
            updateMessage(assistantMessageId, {
              content: accumulatedContent,
              isLoading: true,
            });
          }

          // Mark as complete
          updateMessage(assistantMessageId, {
            isLoading: false,
          });
        // } else {
        //   // Non-streaming mode - COMMENTED OUT
        //   nonStreamingMutation.mutate(request);
        // }
      } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
          // Request was aborted, remove loading message
          setMessages((prev) =>
            prev.filter((msg) => msg.id !== assistantMessageId)
          );
        } else {
          updateMessage(assistantMessageId, {
            content: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
            isLoading: false,
          });
          
          toast({
            title: "Query failed",
            description: error instanceof Error ? error.message : "Failed to get answer",
            variant: "destructive",
          });
        }
      }
    },
    [enableStreaming, addMessage, updateMessage, toast] // removed nonStreamingMutation
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  const addMessageWithAnswer = useCallback(
    (
      query: string,
      answer: string,
      language?: string,
      sources?: Message["sources"]
    ) => {
      // Add user message
      addMessage({
        role: "user",
        content: query,
        language,
      });

      // Add assistant message with pre-computed answer
      addMessage({
        role: "assistant",
        content: answer,
        isLoading: false,
        sources,
      });
    },
    [addMessage]
  );

  return {
    messages,
    setMessages, // Export setMessages for direct manipulation
    sendMessage,
    addMessageWithAnswer,
    clearMessages,
    cancelRequest,
    isLoading: false, // nonStreamingMutation.isPending - always false now (streaming only)
  };
}

