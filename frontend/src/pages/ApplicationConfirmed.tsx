import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { CheckCircle } from "lucide-react";
import logo from "@/assets/logo-purple.svg";

const ApplicationConfirmed = () => {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
      <Link to="/" className="fixed top-8 left-12 z-30 flex items-center gap-3">
        <img src={logo} alt="AI Hiring" className="h-10 w-10" />
        <span className="font-bold text-2xl bg-gradient-primary bg-clip-text text-transparent">AI Hiring</span>
      </Link>

      <div className="w-full max-w-md text-center space-y-6">
        <div className="flex justify-center">
          <CheckCircle className="h-20 w-20 text-green-500" />
        </div>

        <h1 className="text-4xl font-bold">Application Submitted!</h1>

        <p className="text-muted-foreground text-lg">
          Thank you for applying. We've received your application and will review it shortly.
          You'll be contacted via email if you are shortlisted.
        </p>

        <div className="pt-4">
          <Button asChild variant="secondary">
            <Link to="/">Back to Home</Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ApplicationConfirmed;
