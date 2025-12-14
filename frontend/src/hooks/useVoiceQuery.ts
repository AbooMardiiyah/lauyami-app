// NON-STREAMING VERSION - COMMENTED OUT
// Use the streaming approach directly in AppPage.tsx

// import { useMutation } from "@tanstack/react-query";
// import { askWithVoice, VoiceAskRequest } from "@/lib/api";
// import { useToast } from "@/hooks/use-toast";

// export function useVoiceQuery() {
//   const { toast } = useToast();

//   return useMutation({
//     mutationFn: async ({
//       audioFile,
//       language = "en",
//       sessionId,
//       provider = "natlas",
//     }: {
//       audioFile: File;
//       language?: string;
//       sessionId?: string | null;
//       provider?: string;
//     }) => {
//       const request: VoiceAskRequest = {
//         session_id: sessionId || localStorage.getItem("session_id") || null,
//         language,
//         limit: 5,
//         provider,
//       };

//       return askWithVoice(audioFile, request);
//     },
//     onError: (error: Error) => {
//       toast({
//         title: "Voice query failed",
//         description: error.message || "Failed to process voice query",
//         variant: "destructive",
//       });
//     },
//   });
// }

export {}; // Keep file as module

