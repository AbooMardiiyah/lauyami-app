import { Scale, Heart } from "lucide-react";

const Footer = () => {
  return (
    <footer className="py-12 bg-foreground">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl gradient-warm flex items-center justify-center">
              <Scale className="w-5 h-5 text-secondary-foreground" />
            </div>
            <span className="text-xl font-bold text-primary-foreground">Lauya-mi</span>
          </div>

          {/* Tagline */}
          <p className="text-primary-foreground/70 text-center">
            Empowering Nigerian tenants with AI-powered legal understanding
          </p>

          {/* Made with love */}
          <div className="flex items-center gap-2 text-primary-foreground/70">
            <span>Made with</span>
            <Heart className="w-4 h-4 text-secondary fill-secondary" />
            <span>for Nigeria</span>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-primary-foreground/10 text-center">
          <p className="text-sm text-primary-foreground/50">
            © 2025 Lauya-mi. Built for the N-ATLaS Competition.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
