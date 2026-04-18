import { useEffect, useState } from "react";
import { supabase } from "@/supabaseClient";
import AssessmentJobHeader from "@/components/Assessments/AssessmentJobHeader";
import AssessmentOverview from "@/components/Assessments/AssessmentOverview.tsx";
// import AssessmentFilters from "@/components/Assessments/AssessmentFilters.tsx";
import CandidateAssessmentList from "@/components/Assessments/CandidateAssessmentList.tsx";
import CandidateAssessmentDetail from "@/components/Assessments/CandidateAssessmentDetail.tsx";
import { Card } from "@/components/ui/card";

const SHORTLIST_THRESHOLD = 75;

const toNumberOrNull = (value: unknown): number | null => {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

const Assessments = ({ jobId, job }: { jobId?: string; job?: any } = {}) => {
  const [candidates, setCandidates] = useState<any[]>([]);
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
      if (!jobId && !job?.id) {
        setCandidates([]);
        return;
      }
      const id = job?.id ?? jobId;
      try {
        const { data: apps, error } = await supabase
          .from("job_applications")
          .select("*")
          .eq("job_id", id)
          .order("submitted_at", { ascending: false, nullsFirst: false });

        if (error) throw error;

        const normalized = (apps || []).map((a: any) => {
          const score = toNumberOrNull(a.assessment_score);
          return {
            id: a.id || a.applicant_id,
            name: a.name || a.applicant_name || "Unknown",
            email: a.applicant_email || a.email || "",
            invitedDate: a.submitted_at || a.created_at || null,
            assessmentId: a.assessment_id || null,
            assessmentType: a.assessment_type || "AI-generated",
            status: score !== null && score > SHORTLIST_THRESHOLD ? "Shortlisted" : "Rejected",
            score,
            resume: a.resume_url || null,
            notes: a.notes || null,
          };
        }).filter((c: any) => c.score !== null);

        normalized.sort((a, b) => {
          if (a.score === null && b.score === null) return 0;
          if (a.score === null) return 1;
          if (b.score === null) return -1;
          return b.score - a.score;
        });

        setCandidates(normalized);
      } catch (e) {
        console.error("Assessments fetch error:", e);
        setCandidates([]);
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
        assessmentsPending={candidates.filter((c) => c.score === null || c.score === undefined).length}
        assessmentsCompleted={candidates.filter((c) => c.score !== null && c.score !== undefined).length}
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