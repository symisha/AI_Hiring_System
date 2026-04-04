import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import { Building2, Globe, Loader2, Sparkles, Users2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { supabase } from "@/supabaseClient";
import {
  CompanyRecord,
  getAuthenticatedUserEmail,
  getCompanyByEmail,
} from "@/lib/companyOnboarding";
import { companyOnboardingSchema } from "@/lib/validationSchemas";

type CompanyOnboardingFormValues = {
  name?: string;
  industry?: string;
  company_size?: string;
  country?: string;
  description?: string;
};

const industries = [
  "Technology",
  "Finance",
  "Healthcare",
  "Education",
  "Retail",
  "Manufacturing",
  "Consulting",
  "Media",
  "Government",
  "Other",
];

const companySizes = ["1-10", "11-50", "51-200", "201-500", "500+"];
const ONBOARDING_COMPLETE_FLAG = "company_onboarding_completed";

const wizardSteps = [
  {
    title: "Company Basics",
    subtitle: "Set your public company identity",
    icon: Building2,
    fields: ["name", "industry"] as const,
  },
  {
    title: "Organization Size",
    subtitle: "Tell us how large your hiring operation is",
    icon: Users2,
    fields: ["company_size", "country"] as const,
  },
  {
    title: "Brand Story",
    subtitle: "Add a short company description for better matching",
    icon: Sparkles,
    fields: ["description"] as const,
  },
];

const CompanyOnboarding = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState<string>("");
  const [existingCompany, setExistingCompany] = useState<CompanyRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState<string>("");

  const {
    register,
    handleSubmit,
    trigger,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<CompanyOnboardingFormValues>({
    resolver: yupResolver(companyOnboardingSchema),
    mode: "onBlur",
    defaultValues: {
      name: "",
      industry: "",
      company_size: "",
      country: "",
      description: "",
    },
  });

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");

      try {
        const userEmail = await getAuthenticatedUserEmail();
        if (!userEmail) {
          navigate("/hr-login", { replace: true });
          return;
        }

        setEmail(userEmail);

        const company = await getCompanyByEmail(userEmail);
        setExistingCompany(company);

        if (company) {
          reset({
            name: company.name || "",
            industry: company.industry || "",
            company_size: company.company_size || "",
            country: company.country || "",
            description: company.description || "",
          });
        }
      } catch {
        setError("Could not load your company profile. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [navigate, reset]);

  const activeStepMeta = wizardSteps[activeStep];
  const progress = useMemo(() => ((activeStep + 1) / wizardSteps.length) * 100, [activeStep]);

  const nextStep = async () => {
    const fields = [...activeStepMeta.fields] as Array<keyof CompanyOnboardingFormValues>;
    const valid = await trigger(fields);
    if (!valid) return;

    if (activeStep < wizardSteps.length - 1) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const previousStep = () => {
    if (activeStep > 0) {
      setActiveStep((prev) => prev - 1);
    }
  };

  const onSubmit = async (values: CompanyOnboardingFormValues) => {
    setSubmitting(true);
    setError("");

    try {
      const payload = {
        name: values.name?.trim() || "",
        industry: values.industry?.trim() || "",
        email,
        description: values.description?.trim() || "",
        company_size: values.company_size?.trim() || "",
        country: values.country?.trim() || "",
      };

      if (existingCompany?.id) {
        const { error: updateError } = await supabase
          .from("companies")
          .update(payload)
          .eq("id", existingCompany.id);

        if (updateError) throw updateError;
      } else {
        const { error: insertError } = await supabase
          .from("companies")
          .insert(payload);

        if (insertError) throw insertError;
      }

      localStorage.setItem(ONBOARDING_COMPLETE_FLAG, "true");
      navigate("/dashboard", { replace: true });
    } catch {
      setError("Could not save company profile. Please check your Supabase policies and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-muted-foreground">
        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
        Preparing your onboarding wizard...
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-white to-violet-50">
      <div className="w-full min-h-screen">
        <Card className="min-h-screen w-full overflow-hidden rounded-none border-0 shadow-none">
          <div className="grid min-h-screen grid-cols-1 md:grid-cols-3">
            <aside className="bg-[#1a0033] text-slate-100 p-6 md:p-8 md:min-h-screen">
              <div className="flex items-center gap-2 text-violet-300 font-semibold">
                <Globe className="h-4 w-4" />
                Company Setup
              </div>

              <h1 className="mt-4 text-2xl font-bold leading-tight">Welcome to your hiring workspace</h1>
              <p className="mt-3 text-sm text-slate-300">
                Complete these details once so your job posts, branding, and reporting stay consistent.
              </p>

              <div className="mt-8 space-y-3">
                {wizardSteps.map((step, index) => {
                  const Icon = step.icon;
                  const isActive = index === activeStep;
                  const isPassed = index < activeStep;

                  return (
                    <div
                      key={step.title}
                      className={`rounded-lg border px-3 py-2 transition ${
                        isActive
                          ? "border-violet-400 bg-violet-500/10"
                          : isPassed
                            ? "border-slate-700 bg-slate-800"
                            : "border-slate-800 bg-transparent"
                      }`}
                    >
                      <div className="flex items-center gap-2 text-sm font-medium">
                        <Icon className="h-4 w-4" />
                        <span>{step.title}</span>
                      </div>
                      <p className="mt-1 text-xs text-slate-300">{step.subtitle}</p>
                    </div>
                  );
                })}
              </div>
            </aside>

            <section className="md:col-span-2 p-6 md:p-10">
              <div className="mb-6">
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-600 transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="mt-2 text-xs text-muted-foreground">
                  Step {activeStep + 1} of {wizardSteps.length}
                </p>
              </div>

              <h2 className="text-2xl font-semibold">{activeStepMeta.title}</h2>
              <p className="text-sm text-muted-foreground mt-1">{activeStepMeta.subtitle}</p>

              <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
                <div>
                  <label className="text-sm font-medium mb-2 block">Work Email</label>
                  <Input value={email} disabled />
                </div>

                {activeStep === 0 && (
                  <>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Company Name</label>
                      <Input placeholder="e.g. CyberBolt" {...register("name")} />
                      {errors.name && <p className="mt-1 text-xs text-red-500">{errors.name.message}</p>}
                    </div>

                    <div>
                      <label className="text-sm font-medium mb-2 block">Industry</label>
                      <Select
                        value={watch("industry")}
                        onValueChange={(value) => setValue("industry", value, { shouldValidate: true })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select industry" />
                        </SelectTrigger>
                        <SelectContent>
                          {industries.map((industry) => (
                            <SelectItem key={industry} value={industry}>
                              {industry}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {errors.industry && <p className="mt-1 text-xs text-red-500">{errors.industry.message}</p>}
                    </div>
                  </>
                )}

                {activeStep === 1 && (
                  <>
                    <div>
                      <label className="text-sm font-medium mb-2 block">Company Size</label>
                      <Select
                        value={watch("company_size")}
                        onValueChange={(value) => setValue("company_size", value, { shouldValidate: true })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select company size" />
                        </SelectTrigger>
                        <SelectContent>
                          {companySizes.map((size) => (
                            <SelectItem key={size} value={size}>
                              {size}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {errors.company_size && <p className="mt-1 text-xs text-red-500">{errors.company_size.message}</p>}
                    </div>

                    <div>
                      <label className="text-sm font-medium mb-2 block">Country</label>
                      <Input placeholder="e.g. Pakistan" {...register("country")} />
                      {errors.country && <p className="mt-1 text-xs text-red-500">{errors.country.message}</p>}
                    </div>
                  </>
                )}

                {activeStep === 2 && (
                  <div>
                    <label className="text-sm font-medium mb-2 block">Company Description</label>
                    <Textarea
                      rows={6}
                      placeholder="Describe your mission, products, and hiring focus."
                      {...register("description")}
                    />
                    {errors.description && <p className="mt-1 text-xs text-red-500">{errors.description.message}</p>}
                  </div>
                )}

                {error && <p className="text-sm text-red-500">{error}</p>}

                <div className="flex items-center justify-between pt-2">
                  <Button type="button" variant="outline" onClick={previousStep} disabled={activeStep === 0 || submitting}>
                    Back
                  </Button>

                  {activeStep < wizardSteps.length - 1 ? (
                    <Button type="button" onClick={nextStep}>
                      Continue
                    </Button>
                  ) : (
                    <Button type="submit" disabled={submitting}>
                      {submitting ? "Saving profile..." : "Finish Onboarding"}
                    </Button>
                  )}
                </div>
              </form>
            </section>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default CompanyOnboarding;
