import * as yup from "yup";

export const hrLoginSchema = yup.object({
  email: yup.string().trim().email("Enter a valid email address").required("Email is required"),
  password: yup.string().min(6, "Password must be at least 6 characters").required("Password is required"),
});

export const hrSignupSchema = yup.object({
  name: yup.string().trim().min(2, "Full name must be at least 2 characters").required("Full name is required"),
  email: yup.string().trim().email("Enter a valid email address").required("Email is required"),
  password: yup.string().min(8, "Password must be at least 8 characters").required("Password is required"),
  confirm: yup
    .string()
    .oneOf([yup.ref("password")], "Passwords do not match")
    .required("Please confirm your password"),
});

export const candidateLoginSchema = yup.object({
  email: yup.string().trim().email("Enter a valid email address").required("Email is required"),
  password: yup.string().min(6, "Password must be at least 6 characters").required("Password is required"),
});

export const contactSchema = yup.object({
  name: yup.string().trim().min(2, "Name must be at least 2 characters").required("Name is required"),
  email: yup.string().trim().email("Enter a valid email address").required("Email is required"),
  message: yup.string().trim().min(10, "Message must be at least 10 characters").required("Message is required"),
});

export const forgotPasswordSchema = yup.object({
  email: yup.string().trim().email("Enter a valid email address").required("Email is required"),
});

export const resumeFormSchema = yup.object({
  name: yup.string().trim().min(2, "Name must be at least 2 characters").required("Name is required"),
  email: yup.string().trim().email("Enter a valid email address").required("Email is required"),
  phone: yup
    .string()
    .trim()
    .matches(/^[0-9+\-()\s]{7,20}$/, "Enter a valid phone number")
    .required("Phone number is required"),
  resume: yup
    .mixed<FileList>()
    .test("required", "Resume is required", (value) => !!value && value.length > 0),
});

export const jobFormSchema = yup.object({
  title: yup.string().trim().min(3, "Job title must be at least 3 characters").required("Job title is required"),
  description: yup.string().trim().max(2000, "Description must be under 2000 characters").default(""),
});

export const profileSchema = yup.object({
  companyName: yup.string().trim().required("Company name is required"),
  companySize: yup.string().trim().default(""),
  website: yup.string().trim().url("Enter a valid URL (include http:// or https://)").nullable().transform((v) => (v === "" ? null : v)),
  countryCity: yup.string().trim().default(""),
  companyDescription: yup.string().trim().max(2000, "Description must be under 2000 characters").default(""),
  adminName: yup.string().trim().required("Admin name is required"),
  designation: yup.string().trim().default(""),
  adminEmail: yup.string().trim().email("Enter a valid email address").required("Admin email is required"),
  adminPhone: yup
    .string()
    .trim()
    .matches(/^[0-9+\-()\s]{7,20}$/, "Enter a valid phone number")
    .nullable()
    .transform((v) => (v === "" ? null : v)),
});

export const applyBasicInfoSchema = yup.object({
  name: yup.string().trim().min(2, "Full name must be at least 2 characters").required("Full name is required"),
  email: yup.string().trim().email("Enter a valid email address").required("Email is required"),
  phone: yup
    .string()
    .trim()
    .matches(/^[0-9+\-()\s]{7,20}$/, "Enter a valid phone number")
    .nullable()
    .transform((v) => (v === "" ? null : v)),
  linkedin: yup.string().trim().url("LinkedIn must be a valid URL").nullable().transform((v) => (v === "" ? null : v)),
  portfolio: yup.string().trim().url("Portfolio must be a valid URL").nullable().transform((v) => (v === "" ? null : v)),
});
