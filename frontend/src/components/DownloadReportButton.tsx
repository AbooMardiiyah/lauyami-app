import { Download, FileText, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";

interface DownloadReportButtonProps {
  onDownload: (includeAudio: boolean) => void;
  disabled?: boolean;
}

export function DownloadReportButton({ onDownload, disabled }: DownloadReportButtonProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          disabled={disabled}
          className="gap-2"
        >
          <Download className="w-4 h-4" />
          Download report
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-48">
        <DropdownMenuLabel>Choose format</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        <DropdownMenuItem
          onClick={() => onDownload(false)}
          className="cursor-pointer"
        >
          <FileText className="w-4 h-4 mr-2" />
          <div>
            <div className="font-medium">PDF only</div>
            <div className="text-xs text-muted-foreground">Report document</div>
          </div>
        </DropdownMenuItem>
        
        <DropdownMenuItem
          onClick={() => onDownload(true)}
          className="cursor-pointer"
        >
          <Volume2 className="w-4 h-4 mr-2" />
          <div>
            <div className="font-medium">PDF + Audio</div>
            <div className="text-xs text-muted-foreground">With narration</div>
          </div>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
