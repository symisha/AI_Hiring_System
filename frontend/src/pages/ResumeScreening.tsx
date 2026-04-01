import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { supabase } from "@/supabaseClient";
import JobHeader from "@/components/ResumeScreening/JobHeader";
import ScreeningOverview from "@/components/ResumeScreening/ScreeningOverview";

import CandidateList from "@/components/ResumeScreening/CandidateList";
import CandidateDetailPanel from "@/components/ResumeScreening/CandidateDetailPanel";
import { Card } from "@/components/ui/card";

const mockCandidates = [
  {
    id: "c1",
    name: "Alice Johnson",
    email: "alice.j@example.com",
    appliedDate: "2025-11-30",
    experience: 4,
    education: "B.Sc Computer Science",
    skills: ["Node.js", "Postgres", "Docker", "REST"],
    aiScore: 82,
    status: "New",
    resume: "/resumes/alice_johnson.pdf",
    reasons: ["Strong backend experience", "Matches keywords: Node, REST"],
  },
  {
    id: "c2",
    name: "Brian Lee",
    email: "brian.lee@example.com",
    appliedDate: "2025-12-02",
    experience: 7,
    education: "M.Sc Software Engineering",
    skills: ["Python", "Django", "AWS", "Microservices"],
    aiScore: 91,
    status: "Shortlisted",
    resume: "/resumes/brian_lee.pdf",
    reasons: ["Excellent JD alignment", "Cloud + Microservices experience"],
  },
  {
    id: "c3",
    name: "Carmen Diaz",
    email: "carmen.d@example.com",
    appliedDate: "2025-12-04",
    experience: 1,
    education: "B.Eng",
    skills: ["HTML", "CSS", "React"],
    aiScore: 45,
    status: "Rejected",
    resume: "/resumes/carmen_diaz.pdf",
    reasons: ["Insufficient backend experience"],
  },
];

const ResumeScreening = ({ jobId: propJobId, job }: { jobId?: string; job?: any } = {}) => {
  const [candidates, setCandidates] = useState<any[]>(mockCandidates);
  const [searchParams] = useSearchParams();
  const jobId = propJobId ?? searchParams.get("jobId") ?? undefined;
  const [selected, setSelected] = useState<any | null>(null);
  const [jobTitle, setJobTitle] = useState<string>(job?.title || job?.job_title || "");

  useEffect(() => {
    if (!jobId) return;
    // Always fetch fresh title directly from DB
    supabase
      .from("jobs")
      .select("title")
      .eq("id", jobId)
      .single()
      .then(({ data }) => {
        if (data?.title) setJobTitle(data.title);
      });
  }, [jobId]);

  useEffect(() => {
    const fetchApps = async () => {
      if (!jobId) return;
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/routes/dashboard_essentials/job/${jobId}/get-applicants`, {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (!res.ok) throw new Error("Failed to fetch applications");
        const data = await res.json();
        if (data.job_title) setJobTitle(data.job_title);
        // backend returns { total_applicants, applicants }
        const apps = data.applicants || data || [];
        // normalize to expected candidate shape when possible
        const normalized = apps.map((a: any) => ({
          id: a.id || a.applicant_id || a.applicant?.id,
          name: a.name || a.applicant_name || (a.applicant && a.applicant.name) || "Unknown",
          email: a.email || a.applicant_email || (a.applicant && a.applicant.email) || "",
          appliedDate: a.applied_on || a.created_at || null,
          experience: a.experience || null,
          education: a.education || null,
          skills: a.skills || [],
          aiScore: a.resume_score || a.score || null,
          status: a.status || "New",
          resume: a.resume_url || a.resume_path || (a.applicant && a.applicant.resume_url) || null,
          reasons: a.reasons || [],
        }));
        setCandidates(normalized.length ? normalized : mockCandidates);
      } catch (e) {
        console.error("ResumeScreening fetch error:", e);
        setCandidates(mockCandidates);
      }
    };

    fetchApps();
  }, [jobId]);

  return (
    <div>
      <JobHeader jobTitle={jobTitle || (jobId ? `Job ${jobId}` : "Backend Developer")} applicationsCount={candidates.length} />

      <div className="mt-6">
        <div>
          <Card className="p-4">
            <ScreeningOverview candidates={candidates} />

            <div className="mt-6">
              <CandidateList candidates={candidates} onSelect={setSelected} />
            </div>
          </Card>
        </div>
      </div>

      {selected && (
        <CandidateDetailPanel candidate={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
};

export default ResumeScreening;
