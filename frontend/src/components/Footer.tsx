import { Link } from "react-router-dom";
import { Sparkles, Mail, MapPin } from "lucide-react";
import logo from "@/assets/logo-purple.svg"; // adjust path based on your folder

const Footer = () => {
  return (
    <footer className="border-t border-border bg-card/50">
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg">
                <img src={logo} alt="AI Hiring" className="h-8 w-8 object-contain" />
              </div>
              <span className="font-bold text-lg bg-gradient-primary bg-clip-text text-transparent">
                AI Hiring
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Revolutionizing recruitment through intelligent automation and fair AI-powered assessments.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Contact</h3>
            <ul className="space-y-3">
              <li className="flex items-start gap-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4 mt-0.5 text-primary flex-shrink-0" />
                <span>FAST NUCES, Karachi Campus<br />Department of Computer Science</span>
              </li>
              <li className="flex items-center gap-2 text-sm text-muted-foreground">
                <Mail className="h-4 w-4 text-primary flex-shrink-0" />
                <a href="mailto:contact@aihiring.edu" className="hover:text-primary transition-colors">
                  contact@aihiring.edu
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-border text-center text-sm text-muted-foreground">
          <p>© 2025 AI Hiring Automation. Final Year Project - FAST NUCES Karachi.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;