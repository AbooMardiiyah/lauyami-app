import { Button } from "@/components/ui/button";
import { Upload, Mic, MessageCircle, Shield } from "lucide-react";
import { Link } from "react-router-dom";

const HeroSection = () => {
  return (
    <section className="pt-24 pb-16 md:pt-32 md:pb-24 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 gradient-subtle -z-10" />
      <div className="absolute top-20 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl -z-10" />
      <div className="absolute bottom-0 left-0 w-72 h-72 bg-secondary/10 rounded-full blur-3xl -z-10" />

      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6 animate-fade-in">
            <Shield className="w-4 h-4" />
            <span>Powered by N-ATLaS AI</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight animate-slide-up">
            Your Personal{" "}
            <span className="text-gradient">Legal Assistant</span>
            <br />
            for Tenancy Agreements
          </h1>

          {/* Subheadline */}
          <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto animate-slide-up" style={{ animationDelay: "0.1s" }}>
            Upload your agreement, ask questions in <strong>Hausa, Igbo, Yoruba,</strong> or <strong>Nigerian Accented English</strong> — Lauya-mi explains complex legal terms in simple language.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12 animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <Link to="/app">
            <Button variant="hero" size="xl" className="w-full sm:w-auto">
              <Upload className="w-5 h-5" />
              Upload Agreement
            </Button>
            </Link>
            <Link to="/app">
            <Button variant="outline" size="xl" className="w-full sm:w-auto">
              <Mic className="w-5 h-5" />
              Ask with Voice
            </Button>
            </Link>
          </div>

          {/* Feature Pills */}
          <div className="flex flex-wrap items-center justify-center gap-3 animate-slide-up" style={{ animationDelay: "0.3s" }}>
            <div className="flex items-center gap-2 px-4 py-2 bg-card rounded-full shadow-sm border border-border">
              <Upload className="w-4 h-4 text-primary" />
              <span className="text-sm text-muted-foreground">Photo or PDF</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-card rounded-full shadow-sm border border-border">
              <Mic className="w-4 h-4 text-secondary" />
              <span className="text-sm text-muted-foreground">Voice Queries</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-card rounded-full shadow-sm border border-border">
              <MessageCircle className="w-4 h-4 text-accent" />
              <span className="text-sm text-muted-foreground">4 Languages</span>
            </div>
          </div>
        </div>

        {/* Chat Preview Mockup */}
        <div className="mt-16 max-w-3xl mx-auto animate-slide-up" style={{ animationDelay: "0.4s" }}>
          <div className="bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
            {/* Chat Header */}
            <div className="gradient-hero px-6 py-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-foreground/20 flex items-center justify-center">
                <MessageCircle className="w-5 h-5 text-primary-foreground" />
              </div>
              <div>
                <h3 className="font-semibold text-primary-foreground">Lauya-mi</h3>
                <p className="text-sm text-primary-foreground/70">Your AI Legal Assistant</p>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="p-6 space-y-4">
              {/* User Message */}
              <div className="flex justify-end">
                <div className="max-w-[80%] bg-primary/10 rounded-2xl rounded-br-md px-4 py-3">
                  <p className="text-sm text-foreground">
                    Shey landlord le gba owo "caution deposit" mi pada?
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">Yoruba • Voice</p>
                </div>
              </div>

              {/* AI Response */}
              <div className="flex justify-start">
                <div className="max-w-[80%] bg-muted rounded-2xl rounded-bl-md px-4 py-3">
                  <p className="text-sm text-foreground">
                    For your <strong>Caution Deposit</strong>, this agreement says (for Section 5) you get it back <strong>14 days</strong> after you move out, minus money for any damage you cause.
                  </p>
                  <div className="mt-3 p-2 bg-secondary/10 rounded-lg border-l-4 border-secondary">
                    <p className="text-xs text-secondary font-semibold">⚠️ WARNING</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Look at Section 8. You agree to let your landlord increase rent every year. This may be a problem.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Input Area */}
            <div className="px-6 pb-6">
              <div className="flex items-center gap-3 bg-muted rounded-xl px-4 py-3">
                <input
                  type="text"
                  placeholder="Ask about your agreement..."
                  className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
                  disabled
                />
                <button className="w-10 h-10 rounded-full gradient-warm flex items-center justify-center">
                  <Mic className="w-5 h-5 text-secondary-foreground" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
