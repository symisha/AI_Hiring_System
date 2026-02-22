import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";
import image1 from "@/assets/1.jpg";
import logo from "@/assets/logo-purple.svg";
import { supabase } from "@/supabaseClient";

const HRSignup = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);


  // Email/password signup
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (password !== confirm) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });

      if (error) throw error;

      // Optional: redirect user after signup
      // window.location.href = "/user-onboarding";

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Google OAuth signup
  const handleGoogleSignup = async () => {
    setError("");
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: import.meta.env.VITE_SUPABASE_URL, 
        },
      });

      if (error) throw error;
      // Supabase handles the redirect automatically

    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center md:justify-start p-6">
      {/* Top-left logo */}
      <Link to="/" className="fixed top-8 left-12 z-30 flex items-center gap-3">
        <img src={logo} alt="AI Hiring" className="h-10 w-10" />
        <span className="font-bold text-2xl bg-gradient-primary bg-clip-text text-transparent">
          AI Hiring
        </span>
      </Link>

      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch relative z-10">
        {/* Left: signup form */}
        <div className="flex flex-col justify-center px-4 md:pl-20 md:pr-0">
          <div className="w-full max-w-md">
            <div className="text-left mb-6">
              <h2 className="text-3xl font-bold">Create Account</h2>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Full Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium mb-2">Full name</label>
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

              {/* Email */}
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

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-2">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="pl-10 pr-10 bg-secondary border-border"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Confirm Password */}
              <div>
                <label htmlFor="confirm" className="block text-sm font-medium mb-2">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="confirm"
                    type={showConfirm ? "text" : "password"}
                    placeholder="••••••••"
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    required
                    className="pl-10 pr-10 bg-secondary border-border"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm((s) => !s)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                    aria-label={showConfirm ? "Hide password" : "Show password"}
                  >
                    {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Terms */}
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2">
                  <input type="checkbox" className="rounded border-border" />
                  <span className="text-muted-foreground">I agree to the terms and privacy policy</span>
                </label>
              </div>

              {/* Signup button */}
              <Button type="submit" variant="hero" size="lg" className="w-full" disabled={loading}>
                {loading ? "Creating..." : "Create Account"}
              </Button>
            </form>

            {/* OR Divider */}
            <div className="flex items-center my-4 gap-4">
              <hr className="flex-1 border-border" />
              <span className="text-muted-foreground text-sm">OR</span>
              <hr className="flex-1 border-border" />
            </div>

            {/* Google Signup */}
            <Button
              type="button"
              variant="outline"
              size="lg"
              className="w-full flex items-center justify-center gap-2"
              onClick={handleGoogleSignup}
              disabled={loading}
            >
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg"
                alt="Google"
                className="h-5 w-5"
              />
              {loading ? "Redirecting..." : "Sign up with Google"}
            </Button>

            {/* Error message */}
            {error && <p className="text-red-500 mt-2">{error}</p>}

            {/* Login link */}
            <div className="mt-6 text-left">
              <p className="text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link to="/hr-login" className="text-primary hover:underline">
                  Log In
                </Link>
              </p>
            </div>
          </div>
        </div>

        {/* Right image */}
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
