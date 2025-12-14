import { Mic, MessageSquare } from "lucide-react";

const languages = [
  {
    name: "Hausa",
    native: "هَوْسَ",
    example: "Wa ya kamata ya gyara kofar da ta lalace?",
    translation: "Who is supposed to fix the broken door?",
    speakers: "70M+",
  },
  {
    name: "Yoruba",
    native: "Yorùbá",
    example: "Shey landlord le gba owo 'caution deposit' mi pada?",
    translation: "Can the landlord keep my caution deposit?",
    speakers: "45M+",
  },
  {
    name: "Igbo",
    native: "Asụsụ Igbo",
    example: "Kedụ oge m ga-akwụ ụgwọ ụlọ?",
    translation: "When should I pay my rent?",
    speakers: "45M+",
  },
  {
    name: "Nigerian Accented English",
    native: "Naija",
    example: "What is this paper saying about quit notice ehn?",
    translation: "What does this paper say about quit notice?",
    speakers: "100M+",
  },
];

const LanguagesSection = () => {
  return (
    <section id="languages" className="py-16 md:py-24 bg-muted/50">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-2 rounded-full bg-secondary/10 text-secondary text-sm font-medium mb-4">
            Multilingual
          </span>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Speak Your Language
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Lauya-mi understands Nigerian languages. Ask by voice or text — get answers you can understand.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {languages.map((lang, index) => (
            <div
              key={index}
              className="bg-card rounded-2xl p-6 shadow-md border border-border hover:shadow-lg transition-all hover:-translate-y-1"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-foreground">{lang.name}</h3>
                  <p className="text-muted-foreground">{lang.native}</p>
                </div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground bg-muted px-3 py-1 rounded-full">
                  <span>{lang.speakers} speakers</span>
                </div>
              </div>

              {/* Example Query */}
              <div className="bg-muted rounded-xl p-4 mb-3">
                <div className="flex items-center gap-2 mb-2">
                  <Mic className="w-4 h-4 text-secondary" />
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">Voice Query</span>
                </div>
                <p className="text-foreground font-medium">{lang.example}</p>
              </div>

              {/* Translation */}
              <div className="flex items-start gap-2">
                <MessageSquare className="w-4 h-4 text-primary mt-0.5" />
                <p className="text-sm text-muted-foreground italic">{lang.translation}</p>
              </div>
            </div>
          ))}
        </div>

        {/* ASR Note */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-3 bg-card px-6 py-4 rounded-xl shadow-sm border border-border">
            <div className="w-10 h-10 rounded-full gradient-hero flex items-center justify-center">
              <Mic className="w-5 h-5 text-primary-foreground" />
            </div>
            <div className="text-left">
              <p className="font-semibold text-foreground">Powered by N-ATLaS ASR</p>
              <p className="text-sm text-muted-foreground">Industry-leading Nigerian speech recognition</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LanguagesSection;
