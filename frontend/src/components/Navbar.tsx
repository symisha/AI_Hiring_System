import { Link, useLocation } from "react-router-dom";
import { Button } from "./ui/button";
import { Sparkles } from "lucide-react";

const Navbar = () => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-transparent shadow-none border-none">
      <div className="container mx-auto px-6">
        <div className="flex h-16 items-center justify-between">
          {/* <Link to="/" className="flex items-center gap-2 group">
            <div className="bg-gradient-primary p-2 rounded-lg group-hover:shadow-glow transition-all duration-300">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-lg bg-gradient-primary bg-clip-text text-transparent">
              AI Hiring
            </span>
          </Link> */}
          
          <div className="hidden md:flex items-center gap-8">
            <Link
              to="/"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/') ? 'text-primary' : 'text-white'
              }`}
            >
              Home
            </Link>
            <Link
              to="/about"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/about') ? 'text-primary' : 'text-white'
              }`}
            >
              About
            </Link>
            <Link
              to="/contact"
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/contact') ? 'text-primary' : 'text-white'
              }`}
            >
              Contact
            </Link>
          </div>
          
          <div className="flex items-center gap-3">
            <Link to="/hr-login">
              <Button variant="ghost" size="sm">HR Login</Button>
            </Link>
            <Link to="/candidate-login">
              <Button variant="hero" size="sm">Candidate Login</Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;