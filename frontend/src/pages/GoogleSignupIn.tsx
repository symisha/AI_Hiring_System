import { supabase } from "@/supabaseClient";

const signInWithGoogle = async () => {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
  })

  if (error) console.error('Google login error:', error.message)
}
