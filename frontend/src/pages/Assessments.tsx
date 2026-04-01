import { useEffect, useState } from "react";
import { supabase } from "@/supabaseClient";
import AssessmentJobHeader from "@/components/Assessments/AssessmentJobHeader";
import AssessmentOverview from "@/components/Assessments/AssessmentOverview.tsx";
// import AssessmentFilters from "@/components/Assessments/AssessmentFilters.tsx";
import CandidateAssessmentList from "@/components/Assessments/CandidateAssessmentList.tsx";
import CandidateAssessmentDetail from "@/components/Assessments/CandidateAssessmentDetail.tsx";
import { Card } from "@/components/ui/card";

const mockCandidates = [
  {
    id: "a1",
    name: "Alice Johnson",
    email: "alice.j@example.com",
    invitedDate: "2025-12-01",
    // assessmentType: "AI-generated",
    assessmentId: "AS-101",
    status: "Completed",
    score: 87,
    resume: "/resumes/alice_johnson.pdf",
    notes: "Strong backend skills",
  },
  {
    id: "a2",
    name: "Brian Lee",
    email: "brian.lee@example.com",
    invitedDate: "2025-12-03",
    // assessmentType: "Manual",
    assessmentId: "AS-102",
    status: "Pending",
    score: null,
    resume: "/resumes/brian_lee.pdf",
    notes: "Awaiting submission",
  },
  {
    id: "a3",
    name: "Carmen Diaz",
    email: "carmen.d@example.com",
    invitedDate: "2025-12-05",
    // assessmentType: "AI-generated",
    assessmentId: "AS-101",
    status: "Not Started",
    score: null,
    resume: "/resumes/carmen_diaz.pdf",
    notes: "Follow up needed",
  },
];

const Assessments = ({ jobId, job }: { jobId?: string; job?: any } = {}) => {
  const [candidates, setCandidates] = useState<any[]>(mockCandidates);
  const [selected, setSelected] = useState<any | null>(null);
  const [jobTitle, setJobTitle] = useState<string>(job?.title || job?.job_title || "");

  useEffect(() => {
    const id = job?.id ?? jobId;
    if (!id) return;
    supabase
      .from("jobs")
      .select("title")
      .eq("id", id)
      .single()
      .then(({ data }) => {
        if (data?.title) setJobTitle(data.title);
      });
  }, [jobId, job?.id]);

  useEffect(() => {
    const fetchApps = async () => {
      if (!jobId && !job?.id) return;
      const id = job?.id ?? jobId;
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/routes/dashboard_essentials/job/${id}/get-applicants`, {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (!res.ok) throw new Error("Failed to fetch applications");
        const data = await res.json();
        const apps = data.applicants || data || [];
        const normalized = apps.map((a: any) => ({
          id: a.id || a.applicant_id,
          name: a.name || a.applicant_name || (a.applicant && a.applicant.name) || "Unknown",
          email: a.email || (a.applicant && a.applicant.email) || "",
          invitedDate: a.invited_on || a.created_at || null,
          assessmentId: a.assessment_id || null,
          status: a.status || "Pending",
          score: a.resume_score || a.score || null,
          resume: a.resume_url || (a.applicant && a.applicant.resume_url) || null,
          notes: a.notes || null,
        }));
        setCandidates(normalized.length ? normalized : mockCandidates);
      } catch (e) {
        console.error("Assessments fetch error:", e);
        setCandidates(mockCandidates);
      }
    };
    fetchApps();
  }, [jobId, job]);

  return (
    <div>
      <AssessmentJobHeader
        jobTitle={jobTitle || (jobId ? `Job ${jobId}` : "Backend Developer")}
        jobId={job?.id ?? jobId}
        totalInvited={candidates.length}
        assessmentsPending={candidates.filter((c) => c.status === "Pending").length}
        assessmentsCompleted={candidates.filter((c) => c.status === "Completed").length}
        assessmentType="AI-generated"
      />

      <div className="mt-6">
        {/* <div className="lg:col-span-1">
          <AssessmentFilters />
        </div> */}

        <div className="mt-6">
          <Card className="p-4">
            <AssessmentOverview candidates={candidates} />

            <div className="mt-6">
              <CandidateAssessmentList candidates={candidates} onSelect={setSelected} />
            </div>
          </Card>
        </div>
      </div>

      {selected && (
        <CandidateAssessmentDetail candidate={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
};

export default Assessments;
