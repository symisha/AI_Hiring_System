import { ReactElement, useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import {
  getAuthenticatedUserEmail,
  getCompanyByEmail,
  isCompanyProfileComplete,
} from "@/lib/companyOnboarding";

const ONBOARDING_PATH = "/company-onboarding";
const ONBOARDING_COMPLETE_FLAG = "company_onboarding_completed";

type GuardState = "checking" | "ok" | "needs-onboarding";

export const ProtectedRoute = ({ children }: { children: ReactElement }) => {
  const location = useLocation();
  const token = localStorage.getItem("token");
  const hasOnboardingBypass = localStorage.getItem(ONBOARDING_COMPLETE_FLAG) === "true";
  const [guardState, setGuardState] = useState<GuardState>(hasOnboardingBypass ? "ok" : "checking");

  useEffect(() => {
    let mounted = true;

    const checkOnboarding = async () => {
      if (!token) {
        localStorage.removeItem(ONBOARDING_COMPLETE_FLAG);
        if (mounted) setGuardState("checking");
        return;
      }

      // One-time bypass after successful onboarding submit.
      if (hasOnboardingBypass) {
        localStorage.removeItem(ONBOARDING_COMPLETE_FLAG);
        if (mounted) setGuardState("ok");
        return;
      }

      try {
        const email = await getAuthenticatedUserEmail();
        if (!email) {
          localStorage.removeItem(ONBOARDING_COMPLETE_FLAG);
          if (mounted) setGuardState("needs-onboarding");
          return;
        }

        const company = await getCompanyByEmail(email);
        const complete = isCompanyProfileComplete(company);
        if (mounted) {
          localStorage.removeItem(ONBOARDING_COMPLETE_FLAG);
          setGuardState(complete ? "ok" : "needs-onboarding");
        }
      } catch {
        if (mounted) {
          localStorage.removeItem(ONBOARDING_COMPLETE_FLAG);
          setGuardState("needs-onboarding");
        }
      }
    };

    checkOnboarding();

    return () => {
      mounted = false;
    };
  }, [token, hasOnboardingBypass]);

  if (!token) {
    return <Navigate to="/hr-login" replace />;
  }

  if (guardState === "checking") {
    return (
      <div className="min-h-screen flex items-center justify-center text-muted-foreground">
        Loading your workspace...
      </div>
    );
  }

  if (guardState === "needs-onboarding" && location.pathname !== ONBOARDING_PATH) {
    return <Navigate to={ONBOARDING_PATH} replace />;
  }

  if (guardState === "ok" && location.pathname === ONBOARDING_PATH) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default ProtectedRoute;