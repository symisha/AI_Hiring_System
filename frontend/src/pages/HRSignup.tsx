import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Mail, Lock } from "lucide-react";
import image1 from "@/assets/1.jpg";
import logo from "@/assets/logo-purple.svg";

const HRSignup = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Signup logic will be implemented later
    console.log("HR Signup:", { name, email, password, confirm });
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center md:justify-start p-6">
      {/* Top-left logo */}
      <Link to="/" className="fixed top-8 left-12 z-30 flex items-center gap-3">
        <img src={logo} alt="AI Hiring" className="h-10 w-10" />
        <span className="font-bold text-2xl bg-gradient-primary bg-clip-text text-transparent">AI Hiring</span>
      </Link>

      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch relative z-10">
        {/* Left: signup form */}
        <div className="flex flex-col justify-center px-4 md:pl-20 md:pr-0">
          <div className="w-full max-w-md">
            <div className="text-left mb-6">
              <h2 className="text-3xl font-bold">Create Account</h2>
              {/* <p className="text-muted-foreground mt-2">Sign up to create your recruitment dashboard account</p> */}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium mb-2">Full name</label>
                <div className="relative">
                  <Input
                    id="name"
                    type="text"
                    placeholder="Your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="bg-secondary border-border"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-2">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="hr@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="pl-10 bg-secondary border-border"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-2">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="pl-10 bg-secondary border-border"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="confirm" className="block text-sm font-medium mb-2">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="confirm"
                    type="password"
                    placeholder="••••••••"
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    required
                    className="pl-10 bg-secondary border-border"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="rounded border-border" />
                  <span className="text-muted-foreground">I agree to the terms and privacy policy</span>
                </label>
              </div>

              <Button type="submit" variant="hero" size="lg" className="w-full">Create Account</Button>
            </form>

            <div className="mt-6 text-left">
              <p className="text-sm text-muted-foreground">Already have an account? <Link to="/hr-login" className="text-primary hover:underline">Log In</Link></p>
            </div>
          </div>
        </div>

        {/* Right: illustration/image - full right edge (fixed) */}
        <div
          className="hidden md:block fixed top-0 right-0 h-screen w-1/2 bg-cover bg-center"
          style={{ backgroundImage: `url(${image1})` }}
          aria-hidden
        />
      </div>
    </div>
  );
};

export default HRSignup;
