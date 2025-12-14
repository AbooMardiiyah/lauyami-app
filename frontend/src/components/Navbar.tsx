import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Menu, X, Scale, MessageCircle } from "lucide-react";

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl gradient-hero flex items-center justify-center">
              <Scale className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">Lauya-mi</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/" className={`transition-colors ${isActive('/') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}>
              Home
            </Link>
            <Link to="/app" className={`flex items-center gap-2 transition-colors ${isActive('/app') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}>
              <MessageCircle className="w-4 h-4" />
              Chat
            </Link>
            <Link to="/how-it-works" className={`transition-colors ${isActive('/how-it-works') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}>
              How It Works
            </Link>
            <Link to="/languages" className={`transition-colors ${isActive('/languages') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}>
              Languages
            </Link>
            <Link to="/demo" className={`transition-colors ${isActive('/demo') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}>
              Demo
            </Link>
          </div>

          {/* CTA Button */}
          <div className="hidden md:block">
            <Link to="/app">
              <Button variant="hero" size="default">
                Try Lauya-mi Free
              </Button>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-foreground"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 border-t border-border animate-fade-in">
            <div className="flex flex-col gap-4">
              <Link 
                to="/" 
                className={`py-2 transition-colors ${isActive('/') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                onClick={() => setIsOpen(false)}
              >
                Home
              </Link>
              <Link 
                to="/app" 
                className={`flex items-center gap-2 py-2 transition-colors ${isActive('/app') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                onClick={() => setIsOpen(false)}
              >
                <MessageCircle className="w-4 h-4" />
                Chat
              </Link>
              <Link 
                to="/how-it-works" 
                className={`py-2 transition-colors ${isActive('/how-it-works') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                onClick={() => setIsOpen(false)}
              >
                How It Works
              </Link>
              <Link 
                to="/languages" 
                className={`py-2 transition-colors ${isActive('/languages') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                onClick={() => setIsOpen(false)}
              >
                Languages
              </Link>
              <Link 
                to="/demo" 
                className={`py-2 transition-colors ${isActive('/demo') ? 'text-foreground font-semibold' : 'text-muted-foreground hover:text-foreground'}`}
                onClick={() => setIsOpen(false)}
              >
                Demo
              </Link>
              <Link to="/app" onClick={() => setIsOpen(false)}>
                <Button variant="hero" size="default" className="mt-2 w-full">
                  Try Lauya-mi Free
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
