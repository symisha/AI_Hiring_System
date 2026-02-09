import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";
import image1 from "@/assets/1.jpg";
import logo from "@/assets/logo-purple.svg";
import { supabase } from "@/supabaseClient";


const HRLogin = () => {
  const navigate = useNavigate();   
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);


const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError("");
  setLoading(true);

  const { data, error: supabaseError } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (supabaseError) {
    setError(supabaseError.message);
    setLoading(false);
    return;
  }

  const token = data.session?.access_token;
  console.log("Supabase JWT:", token);  //remove this, i think

  if (token) {
    localStorage.setItem("token", token);
    navigate("/dashboard");
  }

  setLoading(false);
};

// Google OAuth login (also handles signup automatically)
const handleGoogleLogin = async () => {
  setError("");
  setLoading(true);

  try {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/dashboard`,
      },
    });

    if (error) throw error;
    // Redirect is handled by Supabase

  } catch (err: any) {
    setError(err.message || "Google login failed");
    setLoading(false);
  }
};


  return (
  <div className="min-h-screen bg-background flex items-center justify-center md:justify-start p-6">
    {/* Top-left logo */}
    <Link to="/" className="fixed top-8 left-12 z-30 flex items-center gap-3">
      <img src={logo} alt="AI Hiring" className="h-10 w-10" />
      <span className="font-bold text-2xl bg-gradient-primary bg-clip-text text-transparent">AI Hiring</span>
    </Link>
  <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch relative z-10">
        {/* Left: HR login form */}
  <div className="flex flex-col justify-center px-4 md:pl-20 md:pr-0">
          

          <div className="w-full max-w-md">
            <div className="text-left mb-6">
              <div className="text-primary mb-2">
                {/* <Sparkles className="h-5 w-5 inline-block" /> */}
              </div>
              <h2 className="text-3xl font-bold">Welcome Back</h2>
              <p className="text-muted-foreground mt-2">Log in to access your recruitment dashboard</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium mb-2">
                    Email Address
                  </label>
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
                  <label htmlFor="password" className="block text-sm font-medium mb-2">
                    Password
                  </label>
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

                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center gap-2">
                    <input type="checkbox" className="rounded border-border" />
                    <span className="text-muted-foreground">Remember me</span>
                  </label>
                <Link
                  to="/forgot-password"
                  className="text-primary hover:underline"
                >
                Forgot password?
                </Link>

                </div>

                <Button type="submit" variant="hero" size="lg" className="w-full">
                  Log In
                </Button>
            </form>

            <div className="mt-6 text-left">
              <p className="text-sm text-muted-foreground">
                Don't have an account?{" "}
                <Link to="/hr-signup" className="text-primary hover:underline">
                  Sign Up
                </Link>
              </p>
            </div>
          </div>

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
              onClick={handleGoogleLogin}
              disabled={loading}
            >
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg"
                alt="Google"
                className="h-5 w-5"
              />
              {loading ? "Redirecting..." : "Sign in with Google"}
            </Button>

          {/* <div className="mt-8 text-left">
            <Link to="/" className="text-sm text-muted-foreground hover:text-primary transition-colors">
              ← Back to Home
            </Link>
          </div> */}
        </div>

        {/* Right: illustration/image - full right edge (fixed) */}
        {/* Fixed background sits behind the content and touches the right edge */}
        <div
          className="hidden md:block fixed top-0 right-0 h-screen w-1/2 bg-cover bg-center"
          style={{ backgroundImage: `url(${image1})` }}
          aria-hidden
        />
      </div>
    </div>
  );
};

export default HRLogin;


 