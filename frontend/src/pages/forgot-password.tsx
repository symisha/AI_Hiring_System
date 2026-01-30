import { useState } from "react";
import { supabase } from "@/supabaseClient";
import { Button } from "@/components/ui/button";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");

  const handleReset = async () => {
    setMessage("");

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: "http://localhost:8081/",
    });

    if (error) {
      setMessage("Error: " + error.message);
    } else {
      setMessage("Password reset email sent. Check your inbox.");
    }
  };

  return (
    <div className="max-w-md mx-auto mt-20 space-y-4">
      <h1 className="text-xl font-bold">Forgot Password</h1>

      <input
        type="email"
        placeholder="Enter your email"
        className="w-full border p-2 rounded"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <Button onClick={handleReset} className="w-full">
        Send Reset Email
      </Button>

      {message && <p className="text-sm">{message}</p>}
    </div>
  );
}
