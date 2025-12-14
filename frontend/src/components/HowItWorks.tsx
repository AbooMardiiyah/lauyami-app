import { Upload, Search, MessageCircle, Shield } from "lucide-react";

const steps = [
  {
    icon: Upload,
    step: "01",
    title: "Upload Your Agreement",
    description: "Take a photo or upload the PDF of your tenancy agreement. Our OCR technology extracts all the text instantly.",
    color: "primary",
  },
  {
    icon: Search,
    step: "02",
    title: "AI Analyzes the Document",
    description: "Lauya-mi reads through the complex legal English and identifies key clauses, potential issues, and your rights.",
    color: "secondary",
  },
  {
    icon: MessageCircle,
    step: "03",
    title: "Ask in Your Language",
    description: "Use voice or text to ask questions in Hausa, Igbo, Yoruba, or Nigerian Accented English. Get clear, simple answers.",
    color: "accent",
  },
  {
    icon: Shield,
    step: "04",
    title: "Know Your Rights",
    description: "Understand what you're signing. Spot predatory clauses before they become problems. Make informed decisions.",
    color: "primary",
  },
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            Simple Process
          </span>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            How Lauya-mi Works
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            From confusion to clarity in four simple steps. No legal background required.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
          {steps.map((item, index) => (
            <div
              key={index}
              className="relative group"
            >
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-12 left-full w-full h-0.5 bg-border -z-10" />
              )}

              <div className="bg-card rounded-2xl p-6 shadow-md border border-border hover:shadow-lg transition-shadow">
                {/* Step Number */}
                <div className="text-5xl font-bold text-muted/50 mb-4">{item.step}</div>

                {/* Icon */}
                <div
                  className={`w-14 h-14 rounded-xl flex items-center justify-center mb-4 ${
                    item.color === "primary"
                      ? "gradient-hero"
                      : item.color === "secondary"
                      ? "gradient-warm"
                      : "bg-accent"
                  }`}
                >
                  <item.icon className={`w-7 h-7 ${item.color === "accent" ? "text-accent-foreground" : "text-primary-foreground"}`} />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-foreground mb-3">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
