import { supabase } from "@/supabaseClient";

export type CompanyRecord = {
  id?: string;
  name: string | null;
  industry: string | null;
  email: string;
  description: string | null;
  company_size: string | null;
  country: string | null;
};

export const requiredCompanyFields: Array<keyof CompanyRecord> = [
  "name",
  "industry",
  "description",
  "company_size",
  "country",
];

export const hasValue = (value: unknown): boolean => {
  if (typeof value === "string") {
    return value.trim().length > 0;
  }
  return value !== null && value !== undefined;
};

export const isCompanyProfileComplete = (company: CompanyRecord | null): boolean => {
  if (!company) return false;
  return requiredCompanyFields.every((field) => hasValue(company[field]));
};

export const getAuthenticatedUserEmail = async (): Promise<string | null> => {
  const { data, error } = await supabase.auth.getUser();
  if (error) return null;
  return data.user?.email ?? null;
};

export const getCompanyByEmail = async (email: string): Promise<CompanyRecord | null> => {
  const { data, error } = await supabase
    .from("companies")
    .select("id, name, industry, email, description, company_size, country")
    .eq("email", email)
    .maybeSingle();

  if (error) {
    throw error;
  }

  return data;
};
