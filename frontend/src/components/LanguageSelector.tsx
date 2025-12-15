import { useState } from "react";
import { Globe, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export interface Language {
  code: string;
  name: string;
  nativeName: string;
}

const SUPPORTED_LANGUAGES: Language[] = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "yo", name: "Yoruba", nativeName: "Yorùbá" },
  { code: "ha", name: "Hausa", nativeName: "Hausa" },
  { code: "ig", name: "Igbo", nativeName: "Igbo" },
];

interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (languageCode: string) => void;
  size?: "sm" | "default";
}

export function LanguageSelector({
  selectedLanguage,
  onLanguageChange,
  size = "default",
}: LanguageSelectorProps) {
  const currentLanguage = SUPPORTED_LANGUAGES.find(
    (lang) => lang.code === selectedLanguage
  ) || SUPPORTED_LANGUAGES[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size={size}
          className="gap-2 bg-background hover:bg-muted border-2 border-foreground/20 hover:border-foreground/40 font-semibold text-foreground shadow-sm"
        >
          <Globe className="w-4 h-4" />
          <span className="font-medium">Select your language</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {SUPPORTED_LANGUAGES.map((lang) => (
          <DropdownMenuItem
            key={lang.code}
            onClick={() => onLanguageChange(lang.code)}
            className="flex items-center justify-between cursor-pointer"
          >
            <div>
              <div className="font-medium">{lang.nativeName}</div>
              <div className="text-xs text-muted-foreground">{lang.name}</div>
            </div>
            {selectedLanguage === lang.code && (
              <Check className="w-4 h-4 text-primary" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export { SUPPORTED_LANGUAGES };

