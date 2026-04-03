import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import logo from "@/assets/logo-purple.svg";
import { supabase } from "@/supabaseClient";

const EmailConfirmationPending = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [checking, setChecking] = useState(true);
  const [message, setMessage] = useState("");

  const email = useMemo(() => {
    const params = new URLSearchParams(location.search);
    return params.get("email") || "your email address";
  }, [location.search]);

  const redirectToLogin = async () => {
    await supabase.auth.signOut();
    navigate("/hr-login", { replace: true });
  };

  const checkConfirmationStatus = async () => {
    setChecking(true);
    setMessage("");

    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error) {
      setChecking(false);
      setMessage("Could not verify confirmation status right now. Please try again.");
      return;
    }

    if (session?.user?.email_confirmed_at) {
      await redirectToLogin();
      return;
    }

    setChecking(false);
    setMessage("Still waiting for email confirmation. Please open the verification link in your inbox.");
  };

  useEffect(() => {
    void checkConfirmationStatus();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (session?.user?.email_confirmed_at) {
        await redirectToLogin();
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="w-full max-w-lg rounded-2xl border border-border bg-card p-8 shadow-lg">
        <Link to="/" className="mb-8 inline-flex items-center gap-3">
          <img src={logo} alt="AI Hiring" className="h-10 w-10" />
          <span className="font-bold text-2xl bg-gradient-primary bg-clip-text text-transparent">
            AI Hiring
          </span>
        </Link>

        <h1 className="text-2xl font-bold">Confirm your email</h1>
        <p className="mt-3 text-muted-foreground">
          We sent a verification link to <span className="font-medium text-foreground">{email}</span>.
          Please confirm your email to continue.
        </p>
        <p className="mt-2 text-muted-foreground">
          Once confirmed, you will be redirected to the login page automatically.
        </p>

        {message && <p className="mt-4 text-sm text-muted-foreground">{message}</p>}

        <div className="mt-6 flex flex-col gap-3 sm:flex-row">
          <Button type="button" variant="hero" onClick={checkConfirmationStatus} disabled={checking}>
            {checking ? "Checking..." : "I have confirmed my email"}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate("/hr-login")}>
            Back to login
          </Button>
        </div>
      </div>
    </div>
  );
};

export default EmailConfirmationPending;
