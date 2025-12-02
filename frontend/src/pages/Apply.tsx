import { useEffect, useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import image1 from "@/assets/1.jpg";
import logo from "@/assets/logo-purple.svg";
import { Mail, User, FileText, Phone } from "lucide-react";

const Apply = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const navigate = useNavigate();

  const [job, setJob] = useState<any | null>(null);

  // Step handling
  const [step, setStep] = useState(1);
  const totalSteps = 3;

  // Form data
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [cover, setCover] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await fetch(import.meta.env.VITE_BACKEND_URL + "/routes/apply?token=" + encodeURIComponent(token));
        if (!res.ok) throw new Error("Invalid token");
        const data = await res.json();
        setJob(data);
      } catch (e) {
        console.error(e);
      }
    })();
  }, [token]);

  const submit = async (e: any) => {
    e.preventDefault();
    if (!token) return alert("Missing token");
    if (!resumeFile) return alert("Please upload a resume");

    const fd = new FormData();
    fd.append("token", token);
    fd.append("name", name);
    fd.append("email", email);
    fd.append("phone", phone);
    fd.append("cover_letter", cover);
    fd.append("resume", resumeFile);

    try {
      const res = await fetch(import.meta.env.VITE_BACKEND_URL + "/routes/apply", {
        method: "POST",
        body: fd,
      });
      const json = await res.json();
      if (res.ok) {
        alert("Application submitted. Thank you!");
        navigate("/");
      } else {
        alert(json.detail || json.message || "Error submitting application");
      }
    } catch (err) {
      console.error(err);
      alert("Error submitting application");
    }
  };

  const nextStep = () => setStep((prev) => Math.min(prev + 1, totalSteps));
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1));

  return (
    <div className="min-h-screen bg-background flex items-center justify-center md:justify-start p-6">
      {/* Logo */}
      <Link to="/" className="fixed top-8 left-12 z-30 flex items-center gap-3">
        <img src={logo} alt="AI Hiring" className="h-10 w-10" />
        <span className="font-bold text-2xl bg-gradient-primary bg-clip-text text-transparent">AI Hiring</span>
      </Link>

      <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-8 items-stretch relative z-10">

        {/* LEFT SIDE — FORM */}
        <div className="flex flex-col justify-center px-4 md:pl-20 md:pr-0">
          <div className="w-full max-w-md">

            {/* Progress Bar */}
            <div className="mb-8">
              <p className="text-sm text-muted-foreground mb-2">
                {step} of {totalSteps} completed
              </p>

              <div className="w-full h-2 rounded-full bg-gray-200">
                <div
                  className="h-2 rounded-full bg-green-500 transition-all"
                  style={{ width: `${(step / totalSteps) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Heading */}
            <h2 className="text-3xl font-bold mb-2">Apply for {job?.title || "the role"}</h2>

            <form onSubmit={submit} className="space-y-6 mt-6">

              {/* STEP 1 — PERSONAL INFO */}
              {step === 1 && (
                <div className="space-y-4 animate-fadeIn">
                  <div>
                    <label className="block text-sm font-medium mb-2">Full Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input placeholder="Full Name" value={name} onChange={(e) => setName(e.target.value)} required className="pl-10 bg-secondary border-border" />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Email</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input placeholder="xyz@gmail.com" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="pl-10 bg-secondary border-border" />
                    </div>
                  </div>

                  <Button onClick={nextStep} type="button" className="w-full">Next</Button>
                </div>
              )}

              {/* STEP 2 — APPLICATION DETAILS */}
              {step === 2 && (
                <div className="space-y-4 animate-fadeIn">
                  <div>
                    <label className="block text-sm font-medium mb-2">Phone</label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input placeholder="+92 XXX-XXXXXXX" value={phone} onChange={(e) => setPhone(e.target.value)} className="pl-10 bg-secondary border-border" />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Cover Letter</label>
                    <textarea placeholder="Type here..." value={cover} onChange={(e) => setCover(e.target.value)} className="w-full rounded-md bg-secondary border-border p-2" rows={5} />
                  </div>

                  <div className="flex justify-between">
                    <Button type="button" onClick={prevStep} variant="secondary">Back</Button>
                    <Button type="button" onClick={nextStep}>Next</Button>
                  </div>
                </div>
              )}

              {/* STEP 3 — UPLOAD DOCUMENTS */}
              {step === 3 && (
                <div className="space-y-4 animate-fadeIn">
                  <div>
                    <label className="block text-sm font-medium mb-2">Resume (PDF/DOC)</label>
                    <div className="relative">
                      <FileText className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <input required type="file" accept=".pdf,.doc,.docx"
                        onChange={(e) => setResumeFile(e.target.files ? e.target.files[0] : null)}
                        className="pl-10" />
                    </div>
                  </div>

                  <div className="flex justify-between">
                    <Button type="button" onClick={prevStep} variant="secondary">Back</Button>
                    <Button type="submit">Submit Application</Button>
                  </div>
                </div>
              )}

            </form>

            {/* <div className="mt-6 text-left">
              <p className="text-sm text-muted-foreground">
                Have an account? <Link to="/candidate-login" className="text-primary hover:underline">Sign In</Link>
              </p>
            </div> */}

          </div>
        </div>

        {/* RIGHT IMAGE */}
        <div
          className="hidden md:block fixed top-0 right-0 h-screen w-1/2 bg-cover bg-center"
          style={{ backgroundImage: `url(${image1})` }}
        />
      </div>
    </div>
  );
};

export default Apply;
