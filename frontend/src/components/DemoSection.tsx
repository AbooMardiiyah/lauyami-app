import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Upload, FileText, Mic, Send, AlertTriangle, CheckCircle } from "lucide-react";

const demoMessages = [
  {
    role: "user",
    content: "What is this paper saying about quit notice ehn?",
    language: "Nigerian Accented English",
  },
  {
    role: "assistant",
    content: `Based on your tenancy agreement (Section 12), your landlord must give you **6 months notice** before asking you to leave.

**Important:** This notice can only be given AFTER your current rent period ends. If your rent runs until January 2026, the notice period starts counting from February 2026.

✅ **Your Right:** Under Lagos Tenancy Law, a yearly tenant is entitled to 6 months notice.

⚠️ **Warning Found:** Section 15 says you "waive your right to notice to quit." This clause may not be enforceable under Nigerian law — but it's something to discuss with a lawyer before signing.`,
  },
];

const DemoSection = () => {
  const [activeTab, setActiveTab] = useState<"upload" | "chat">("chat");

  return (
    <section id="demo" className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <span className="inline-block px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            Interactive Demo
          </span>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            See Lauya-mi in Action
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload a document and ask questions — experience the power of AI-assisted legal understanding.
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Tabs */}
          <div className="flex items-center justify-center gap-2 mb-8">
            <button
              onClick={() => setActiveTab("upload")}
              className={`px-6 py-3 rounded-xl font-medium transition-all ${
                activeTab === "upload"
                  ? "gradient-hero text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              <Upload className="w-4 h-4 inline-block mr-2" />
              Upload
            </button>
            <button
              onClick={() => setActiveTab("chat")}
              className={`px-6 py-3 rounded-xl font-medium transition-all ${
                activeTab === "chat"
                  ? "gradient-hero text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              <Mic className="w-4 h-4 inline-block mr-2" />
              Chat Demo
            </button>
          </div>

          {/* Content */}
          <div className="bg-card rounded-2xl shadow-lg border border-border overflow-hidden">
            {activeTab === "upload" ? (
              <div className="p-8 md:p-12">
                <div className="border-2 border-dashed border-border rounded-xl p-12 text-center hover:border-primary/50 transition-colors cursor-pointer">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                    <FileText className="w-8 h-8 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold text-foreground mb-2">
                    Drop your agreement here
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Supports PDF, JPG, PNG — or take a photo
                  </p>
                  <Button variant="outline">
                    <Upload className="w-4 h-4 mr-2" />
                    Browse Files
                  </Button>
                </div>

                <div className="mt-6 grid grid-cols-3 gap-4 text-center">
                  <div className="p-4 bg-muted rounded-xl">
                    <CheckCircle className="w-5 h-5 mx-auto mb-2 text-success" />
                    <p className="text-sm text-muted-foreground">OCR Extraction</p>
                  </div>
                  <div className="p-4 bg-muted rounded-xl">
                    <CheckCircle className="w-5 h-5 mx-auto mb-2 text-success" />
                    <p className="text-sm text-muted-foreground">Clause Analysis</p>
                  </div>
                  <div className="p-4 bg-muted rounded-xl">
                    <CheckCircle className="w-5 h-5 mx-auto mb-2 text-success" />
                    <p className="text-sm text-muted-foreground">Risk Detection</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col h-[500px]">
                {/* Chat Header */}
                <div className="gradient-hero px-6 py-4 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary-foreground/20 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-primary-foreground" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-primary-foreground">Tenancy Agreement Analysis</h3>
                    <p className="text-sm text-primary-foreground/70">Sample_Tenancy_Agreement.pdf • 12 pages</p>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  {demoMessages.map((msg, index) => (
                    <div
                      key={index}
                      className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-2xl px-5 py-4 ${
                          msg.role === "user"
                            ? "bg-primary/10 rounded-br-md"
                            : "bg-muted rounded-bl-md"
                        }`}
                      >
                        {msg.role === "user" && (
                          <p className="text-xs text-muted-foreground mb-2">
                            {msg.language} • Voice
                          </p>
                        )}
                        <div className="text-foreground whitespace-pre-line text-sm leading-relaxed">
                          {msg.content.split("**").map((part, i) =>
                            i % 2 === 1 ? (
                              <strong key={i}>{part}</strong>
                            ) : (
                              <span key={i}>{part}</span>
                            )
                          )}
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Warning Banner */}
                  <div className="flex items-start gap-3 p-4 bg-secondary/10 rounded-xl border border-secondary/20">
                    <AlertTriangle className="w-5 h-5 text-secondary flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-semibold text-foreground text-sm">Predatory Clause Detected</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Section 15 attempts to waive your statutory right to notice. Consider negotiating this term.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Input */}
                <div className="p-4 border-t border-border">
                  <div className="flex items-center gap-3 bg-muted rounded-xl px-4 py-3">
                    <input
                      type="text"
                      placeholder="Ask about your agreement..."
                      className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
                    />
                    <button className="w-10 h-10 rounded-full gradient-warm flex items-center justify-center hover:scale-105 transition-transform">
                      <Mic className="w-5 h-5 text-secondary-foreground" />
                    </button>
                    <button className="w-10 h-10 rounded-full gradient-hero flex items-center justify-center hover:scale-105 transition-transform">
                      <Send className="w-5 h-5 text-primary-foreground" />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default DemoSection;
