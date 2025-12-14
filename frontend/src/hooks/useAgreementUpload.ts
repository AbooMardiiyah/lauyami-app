// NON-STREAMING VERSION - COMMENTED OUT
// Use useAgreementUploadStream instead

// import { useMutation } from "@tanstack/react-query";
// import { uploadAgreement, UploadAgreementResponse } from "@/lib/api";
// import { useToast } from "@/hooks/use-toast";

// export function useAgreementUpload() {
//   const { toast } = useToast();

//   return useMutation({
//     mutationFn: async ({
//       file,
//       language = "en",
//     }: {
//       file: File;
//       language?: string;
//     }): Promise<UploadAgreementResponse> => {
//       return uploadAgreement(file, language);
//     },
//     onSuccess: (data) => {
//       // Store session_id in localStorage
//       localStorage.setItem("session_id", data.session_id);
//       localStorage.setItem("document_id", data.document_id);
      
//       toast({
//         title: "Document uploaded successfully",
//         description: "Your agreement has been analyzed. You can now ask questions!",
//       });
//     },
//     onError: (error: Error) => {
//       toast({
//         title: "Upload failed",
//         description: error.message || "Failed to upload document",
//         variant: "destructive",
//       });
//     },
//   });
// }

export {}; // Keep file as module

