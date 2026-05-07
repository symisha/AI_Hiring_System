import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import logo from "@/assets/logo-purple.svg";
import { Mail, User, FileText, Phone } from "lucide-react";
import { applyBasicInfoSchema } from "@/lib/validationSchemas";

const Apply: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const sectionLabels = [
    "Basic Information",
    "Education",
    "Experience",
    "Skills",
    "Projects",
    "CNIC",
    "Declaration",
  ];
  const totalSteps = sectionLabels.length;

  const [step, setStep] = useState(1);
  const [stepError, setStepError] = useState("");

  // Basic info
  // const [jobID, setJobID] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [city, setCity] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [portfolio, setPortfolio] = useState("");

  // Education
  const [degree, setDegree] = useState("");
  const [major, setMajor] = useState("");
  const [university, setUniversity] = useState("");
  const [gradYear, setGradYear] = useState("");
  const [cgpa, setCgpa] = useState("");

  // Experience
  type Exp = {
    id: string;
    company: string;
    role: string;
    startDate: string; // yyyy-mm
    endDate: string; // yyyy-mm
    isCurrent?: boolean;
    years?: string;
  };
  const [experiences, setExperiences] = useState<Exp[]>([
    { id: "e-1", company: "", role: "", startDate: "", endDate: "", isCurrent: false, years: "0" },
  ]);

  // Skills
  const skillOptions = {
    languages: ["JavaScript", "TypeScript", "Python", "Java", "C++"],
    frameworks: ["React", "Node", "Express", "Django", "Flask"],
    databases: ["PostgreSQL", "MySQL", "MongoDB", "SQLite"],
    tools: ["Git", "Docker", "Kubernetes", "AWS"],
    soft: ["Communication", "Teamwork", "Problem Solving"],
  } as const;
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [customSkill, setCustomSkill] = useState("");

  // Projects
  type Project = { id: string; title: string; desc: string; tech: string; link: string };
  const [projects, setProjects] = useState<Project[]>([
    { id: "p-1", title: "", desc: "", tech: "", link: "" },
  ]);

  // Declaration + resume
  const [agreed, setAgreed] = useState(false);
  const [cnicImageFile, setCnicImageFile] = useState<File | null>(null);

  const nextStep = async () => {
    setStepError("");
    if (step === 1) {
      try {
        await applyBasicInfoSchema.validate(
          { name, email, phone, linkedin, portfolio },
          { abortEarly: false }
        );
      } catch (err: any) {
        setStepError(err?.errors?.[0] || "Please complete required fields.");
        return;
      }
    }

    if (step === 6) {
      if (!cnicImageFile) {
        setStepError("Please upload your CNIC image.");
        return;
      }
      if (!cnicImageFile.type.startsWith("image/")) {
        setStepError("CNIC must be an image file.");
        return;
      }
    }
    setStep((s) => Math.min(s + 1, totalSteps));
  };
  const prevStep = () => setStep((s) => Math.max(s - 1, 1));

  // Experience helpers
  const addExperience = () => {
    if (experiences.length >= 10) return;
    setExperiences((s) => [...s, { id: `e-${Date.now()}`, company: "", role: "", startDate: "", endDate: "", isCurrent: false, years: "0" }]);
  };
  const removeExperience = (id: string) => setExperiences((s) => s.filter((e) => e.id !== id));
  const calcYears = (exp: Exp) => {
    if (!exp.startDate) return "0";
    const start = new Date(exp.startDate + "-01");
    const end = exp.isCurrent || !exp.endDate ? new Date() : new Date(exp.endDate + "-01");
    const diff = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
    return diff > 0 ? (Math.round(diff * 10) / 10).toString() : "0";
  };
  const updateExperience = (id: string, patch: Partial<Exp>) => {
    setExperiences((s) => s.map((e) => (e.id === id ? { ...e, ...patch, years: calcYears({ ...e, ...patch }) } : e)));
  };

  // Skills helpers
  const toggleSkill = (s: string) => setSelectedSkills((c) => (c.includes(s) ? c.filter((x) => x !== s) : [...c, s]));
  const addCustomSkill = () => {
    const s = customSkill.trim();
    if (!s) return;
    setSelectedSkills((c) => (c.includes(s) ? c : [...c, s]));
    setCustomSkill("");
  };

  // Projects helpers
  const addProject = () => {
    if (projects.length >= 3) return;
    setProjects((p) => [...p, { id: `p-${Date.now()}`, title: "", desc: "", tech: "", link: "" }]);
  };
  const updateProject = (id: string, patch: Partial<Project>) => setProjects((p) => p.map((pr) => (pr.id === id ? { ...pr, ...patch } : pr)));
  const removeProject = (id: string) => setProjects((p) => p.filter((pr) => pr.id !== id));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStepError("");
    try {
      await applyBasicInfoSchema.validate(
        { name, email, phone, linkedin, portfolio },
        { abortEarly: false }
      );
    } catch (err: any) {
      setStep(1);
      setStepError(err?.errors?.[0] || "Please complete required fields.");
      return;
    }
    if (!cnicImageFile) {
      setStep(6);
      setStepError("Please upload your CNIC image.");
      return;
    }
    if (!agreed) return alert("Please agree to the terms and consent");
    if (!token) return alert("Invalid application link. Please use the link provided to you.");

    const fd = new FormData();
    fd.append("token", token);
    fd.append("name", name);
    fd.append("email", email);
    fd.append("phone", phone);
    fd.append("city", city);
    fd.append("linkedin", linkedin);
    fd.append("portfolio", portfolio);

    fd.append("cnic_image", cnicImageFile);

    fd.append("degree", degree);
    fd.append("major", major);
    fd.append("university", university);
    fd.append("grad_year", gradYear);
    fd.append("cgpa", cgpa);

    fd.append("experiences", JSON.stringify(experiences));
    fd.append("skills", JSON.stringify(selectedSkills));
    fd.append("projects", JSON.stringify(projects));

    try {
      const res = await fetch(import.meta.env.VITE_BACKEND_URL + "/routes/apply/form", {
        method: "POST",
        body: fd,
      });
      const json = await res.json();
      if (res.ok) {
        navigate("/apply/confirmed");
      } else {
        alert(json.detail || json.message || "Error submitting application");
      }
    } catch (err) {
      console.error(err);
      alert("Error submitting application");
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-start justify-center p-6">
      <Link to="/" className="fixed top-8 left-12 z-30 flex items-center gap-3">
        <img src={logo} alt="AI Hiring" className="h-10 w-10" />
        <span className="font-bold text-2xl bg-gradient-primary bg-clip-text text-transparent">AI Hiring</span>
      </Link>

      <div className="w-full max-w-4xl mx-auto py-8">
        <div className="mb-6">
          <p className="text-sm text-muted-foreground mb-2">{sectionLabels[step - 1]}</p>
          <div className="w-full h-2 rounded-full bg-gray-200">
            <div className="h-2 rounded-full bg-green-500 transition-all" style={{ width: `${(step / totalSteps) * 100}%` }} />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground mt-2">
            {sectionLabels.map((s, i) => (
              <div key={s} className={`px-1 ${i + 1 === step ? "font-medium" : ""}`}>{i + 1}. {s.split(" ")[0]}</div>
            ))}
          </div>
        </div>

        <h2 className="text-3xl font-bold mb-4">Apply for the Job</h2>

        <form onSubmit={submit} className="space-y-6">
          {stepError && <p className="text-sm text-red-500">{stepError}</p>}
          {step === 1 && (
            <div className="space-y-4">
              {/* <div>
                <label className="block text-sm font-medium mb-2">Job ID</label>
                <div className="relative">
                  <Hash className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input placeholder="Enter Job ID" value={jobID} onChange={(e) => setJobID(e.target.value)} required className="pl-10 bg-secondary border-border" />
                </div>
              </div> */}

              <div>
                <label className="block text-sm font-medium mb-2">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input placeholder="Full Name" value={name} onChange={(e) => setName(e.target.value)} required className="pl-10 bg-secondary border-border" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="xyz@gmail.com" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="pl-10 bg-secondary border-border" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Phone</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} className="pl-10 bg-secondary border-border" />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">City / Location</label>
                  <Input placeholder="City" value={city} onChange={(e) => setCity(e.target.value)} className="bg-secondary border-border" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">LinkedIn (optional)</label>
                  <Input placeholder="LinkedIn URL" value={linkedin} onChange={(e) => setLinkedin(e.target.value)} className="bg-secondary border-border" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Portfolio / GitHub (optional)</label>
                  <Input placeholder="Portfolio or GitHub" value={portfolio} onChange={(e) => setPortfolio(e.target.value)} className="bg-secondary border-border" />
                </div>
              </div>

              <div className="flex justify-end">
                <Button type="button" onClick={nextStep} className="w-40">Next</Button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Degree</label>
                  <Input placeholder="BS / MS / BBA etc." value={degree} onChange={(e) => setDegree(e.target.value)} className="bg-secondary border-border" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Field / Major</label>
                  <Input placeholder="Computer Science" value={major} onChange={(e) => setMajor(e.target.value)} className="bg-secondary border-border" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">University</label>
                  <Input placeholder="University name" value={university} onChange={(e) => setUniversity(e.target.value)} className="bg-secondary border-border" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Graduation Year</label>
                  <Input placeholder="2024" value={gradYear} onChange={(e) => setGradYear(e.target.value)} className="bg-secondary border-border" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">CGPA / Percentage</label>
                  <Input placeholder="3.5 / 85%" value={cgpa} onChange={(e) => setCgpa(e.target.value)} className="bg-secondary border-border" />
                </div>
              </div>

              <div className="flex justify-between">
                <Button type="button" onClick={prevStep} variant="secondary">Back</Button>
                <Button type="button" onClick={nextStep}>Next</Button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              {experiences.map((exp, idx) => (
                <div key={exp.id} className="border p-3 rounded-md">
                  <div className="flex justify-between items-center mb-2">
                    <div className="text-sm font-medium">Experience #{idx + 1}</div>
                    <div className="flex gap-2">
                      {experiences.length > 1 && (
                        <Button variant="secondary" type="button" onClick={() => removeExperience(exp.id)}>Remove</Button>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <Input placeholder="Company" value={exp.company} onChange={(e) => updateExperience(exp.id, { company: e.target.value })} />
                    <Input placeholder="Role / Title" value={exp.role} onChange={(e) => updateExperience(exp.id, { role: e.target.value })} />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mt-3 items-center">
                    <div>
                      <label className="text-xs">Start</label>
                      <Input type="month" value={exp.startDate} onChange={(e) => updateExperience(exp.id, { startDate: e.target.value })} />
                    </div>
                    <div>
                      <label className="text-xs">End</label>
                      <Input type="month" value={exp.endDate} onChange={(e) => updateExperience(exp.id, { endDate: e.target.value, isCurrent: false })} />
                    </div>
                    <div className="flex items-center gap-2">
                      <input id={`cur-${exp.id}`} type="checkbox" checked={!!exp.isCurrent} onChange={(e) => updateExperience(exp.id, { isCurrent: e.target.checked })} />
                      <label htmlFor={`cur-${exp.id}`}>Currently working</label>
                    </div>
                    <div className="text-sm">Years: {exp.years || calcYears(exp)}</div>
                  </div>
                </div>
              ))}

              <div className="flex gap-2">
                <Button type="button" onClick={addExperience}>Add Experience</Button>
              </div>

              <div className="flex justify-between">
                <Button type="button" onClick={prevStep} variant="secondary">Back</Button>
                <Button type="button" onClick={nextStep}>Next</Button>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              <div>
                <div className="text-sm font-medium mb-2">Programming Languages</div>
                <div className="flex flex-wrap gap-2">
                  {skillOptions.languages.map((s) => (
                    <label key={s} className="flex items-center gap-2">
                      <input type="checkbox" checked={selectedSkills.includes(s)} onChange={() => toggleSkill(s)} />
                      <span>{s}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <div className="text-sm font-medium mb-2">Frameworks</div>
                <div className="flex flex-wrap gap-2">
                  {skillOptions.frameworks.map((s) => (
                    <label key={s} className="flex items-center gap-2">
                      <input type="checkbox" checked={selectedSkills.includes(s)} onChange={() => toggleSkill(s)} />
                      <span>{s}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium mb-2">Databases / Tools</div>
                  <div className="flex flex-wrap gap-2">
                    {[...skillOptions.databases, ...skillOptions.tools].map((s) => (
                      <label key={s} className="flex items-center gap-2">
                        <input type="checkbox" checked={selectedSkills.includes(s)} onChange={() => toggleSkill(s)} />
                        <span>{s}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium mb-2">Soft Skills</div>
                  <div className="flex flex-wrap gap-2">
                    {skillOptions.soft.map((s) => (
                      <label key={s} className="flex items-center gap-2">
                        <input type="checkbox" checked={selectedSkills.includes(s)} onChange={() => toggleSkill(s)} />
                        <span>{s}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex gap-2 mt-2">
                <Input placeholder="Add custom skill" value={customSkill} onChange={(e) => setCustomSkill(e.target.value)} />
                <Button type="button" onClick={addCustomSkill}>Add</Button>
              </div>

              {selectedSkills.length > 0 && (
                <div className="mt-4 p-3 bg-secondary rounded-md">
                  <div className="text-sm font-medium mb-2">Selected Skills ({selectedSkills.length})</div>
                  <div className="flex flex-wrap gap-2">
                    {selectedSkills.map((skill) => (
                      <div key={skill} className="flex items-center gap-2 bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm">
                        <span>{skill}</span>
                        <button
                          type="button"
                          onClick={() => setSelectedSkills((c) => c.filter((x) => x !== skill))}
                          className="ml-1 font-bold hover:opacity-70"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-between">
                <Button type="button" onClick={prevStep} variant="secondary">Back</Button>
                <Button type="button" onClick={nextStep}>Next</Button>
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-4">
              {projects.map((pr, idx) => (
                <div key={pr.id} className="border p-3 rounded-md">
                  <div className="flex justify-between items-center mb-2">
                    <div className="text-sm font-medium">Project #{idx + 1}</div>
                    <div className="flex gap-2">
                      {projects.length > 1 && <Button variant="secondary" type="button" onClick={() => removeProject(pr.id)}>Remove</Button>}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    <Input placeholder="Project Title" value={pr.title} onChange={(e) => updateProject(pr.id, { title: e.target.value })} />
                    <textarea placeholder="Description" value={pr.desc} onChange={(e) => updateProject(pr.id, { desc: e.target.value })} className="w-full rounded-md bg-secondary border-border p-2" rows={3} />
                    <Input placeholder="Tech stack (comma separated)" value={pr.tech} onChange={(e) => updateProject(pr.id, { tech: e.target.value })} />
                    <Input placeholder="GitHub or Live link (optional)" value={pr.link} onChange={(e) => updateProject(pr.id, { link: e.target.value })} />
                  </div>
                </div>
              ))}

              <div className="flex gap-2">
                <Button type="button" onClick={addProject}>Add Project</Button>
              </div>

              <div className="flex justify-between">
                <Button type="button" onClick={prevStep} variant="secondary">Back</Button>
                <Button type="button" onClick={nextStep}>Next</Button>
              </div>
            </div>
          )}

          {step === 6 && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">CNIC Image</label>
                <div className="relative">
                  <FileText className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setCnicImageFile(e.target.files ? e.target.files[0] : null)}
                    className="pl-10 bg-secondary border-border"
                  />
                </div>
                {cnicImageFile && (
                  <p className="text-xs text-muted-foreground mt-2">Selected: {cnicImageFile.name}</p>
                )}
              </div>

              <div className="flex justify-between">
                <Button type="button" onClick={prevStep} variant="secondary">Back</Button>
                <Button type="button" onClick={nextStep}>Next</Button>
              </div>
            </div>
          )}

          {step === 7 && (
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <input id="agree" type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
                <label htmlFor="agree" className="text-sm">I agree to the terms and consent to data usage for recruitment purposes.</label>
              </div>

              <div className="flex justify-between">
                <Button type="button" onClick={prevStep} variant="secondary">Back</Button>
                <Button type="submit" disabled={!agreed}>Submit Application</Button>
              </div>
            </div>
          )}

        </form>
      </div>
    </div>
  );
};

export default Apply;
