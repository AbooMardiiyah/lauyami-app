import { CheckCircle, AlertTriangle } from "lucide-react";
import { parseAnalysisText, ParsedSection } from "@/lib/analysisParser";

interface AnalysisDisplayProps {
  analysisText: string;
}

export function AnalysisDisplay({ analysisText }: AnalysisDisplayProps) {
  const sections = parseAnalysisText(analysisText);
  
  console.log("[AnalysisDisplay] Received text length:", analysisText.length);
  console.log("[AnalysisDisplay] Parsed sections:", sections.length);

  if (sections.length === 0) {
    console.log("[AnalysisDisplay] No sections parsed, showing raw text");
    return (
      <div className="whitespace-pre-wrap text-sm text-foreground">
        {analysisText}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {sections.map((section, index) => (
        <SectionCard key={index} section={section} />
      ))}
    </div>
  );
}

function SectionCard({ section }: { section: ParsedSection }) {
  switch (section.type) {
    case 'intro':
      return (
        <p className="text-base font-medium text-foreground mb-4 leading-relaxed">
          {section.content}
        </p>
      );

    case 'right':
      return (
        <div className="mb-4 p-4 bg-green-50 dark:bg-green-950/20 rounded-xl border border-green-200 dark:border-green-900/30">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-green-900 dark:text-green-100 text-sm mb-1">
                Your Right
              </p>
              <p className="text-sm text-green-800 dark:text-green-200 leading-relaxed">
                {section.content}
              </p>
            </div>
          </div>
        </div>
      );

    case 'warning':
      return (
        <div className="mb-4 p-4 bg-yellow-50 dark:bg-yellow-950/20 rounded-xl border border-yellow-200 dark:border-yellow-900/30">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-yellow-900 dark:text-yellow-100 text-sm mb-1">
                Warning Found
              </p>
              <p className="text-sm text-yellow-800 dark:text-yellow-200 leading-relaxed">
                {section.content}
              </p>
            </div>
          </div>
        </div>
      );

    case 'predatory':
      return (
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-950/20 rounded-xl border border-red-200 dark:border-red-900/30">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900 dark:text-red-100 text-sm mb-1">
                Predatory Clause Detected
              </p>
              <p className="text-sm text-red-800 dark:text-red-200 leading-relaxed">
                {section.content}
              </p>
            </div>
          </div>
        </div>
      );

    case 'text':
      return (
        <p className="text-sm text-foreground mb-2 leading-relaxed">
          {section.content}
        </p>
      );

    default:
      return null;
  }
}

