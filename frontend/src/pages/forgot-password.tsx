import { useState } from "react";
import { supabase } from "@/supabaseClient";
import { Button } from "@/components/ui/button";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { forgotPasswordSchema } from "@/lib/validationSchemas";

type ForgotPasswordFormValues = {
  email: string;
};

export default function ForgotPassword() {
  const [message, setMessage] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormValues>({
    resolver: yupResolver(forgotPasswordSchema),
    mode: "onChange",
    reValidateMode: "onChange",
    defaultValues: {
      email: "",
    },
  });

  const handleReset = async (values: ForgotPasswordFormValues) => {
    setMessage("");

    const { error } = await supabase.auth.resetPasswordForEmail(values.email, {
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

      <form onSubmit={handleSubmit(handleReset)} className="space-y-2">
        <input
          type="email"
          placeholder="Enter your email"
          className="w-full border p-2 rounded"
          {...register("email")}
        />
        {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}

        <Button type="submit" className="w-full">
          Send Reset Email
        </Button>
      </form>

      {message && <p className="text-sm">{message}</p>}
    </div>
  );
}
