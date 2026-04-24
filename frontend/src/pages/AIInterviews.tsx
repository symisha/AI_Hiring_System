import { useEffect, useState } from "react";
import { supabase } from "@/supabaseClient";
import AIInterviewJobHeader from "@/components/AIInterviews/AIInterviewJobHeader";
import AIInterviewOverview from "@/components/AIInterviews/AIInterviewOverview.tsx";
// import AIInterviewFilters from "@/components/AIInterviews/AIInterviewFilters.tsx";
import CandidateInterviewList from "@/components/AIInterviews/CandidateInterviewList.tsx";
import CandidateInterviewDetail from "@/components/AIInterviews/CandidateInterviewDetail.tsx";
import { Card } from "@/components/ui/card";

const SHORTLIST_THRESHOLD = 45;

const toNumberOrNull = (value: unknown): number | null => {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

const AIInterviews = ({ jobId, job }: { jobId?: string; job?: any } = {}) => {
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
          const interviewScore = toNumberOrNull(a.interview_score);
          return {
            id: a.id || a.applicant_id,
            name: a.name || a.applicant_name || "Unknown",
            email: a.applicant_email || a.email || "",
            invitedDate: a.submitted_at || a.created_at || null,
            interviewStatus: interviewScore !== null && interviewScore > SHORTLIST_THRESHOLD ? "Shortlisted" : "Rejected",
            interviewScore,
            assessmentScore: toNumberOrNull(a.assessment_score),
            aiScore: interviewScore,
            communication: toNumberOrNull(a.communication),
            confidence: toNumberOrNull(a.confidence),
            fitLabel: interviewScore !== null && interviewScore > SHORTLIST_THRESHOLD ? "Strong Fit" : "Rejected",
            transcript: a.transcript || null,
            media: a.media || null,
          };
        }).filter((c: any) => c.interviewScore !== null);

        normalized.sort((a, b) => {
          if (a.interviewScore === null && b.interviewScore === null) return 0;
          if (a.interviewScore === null) return 1;
          if (b.interviewScore === null) return -1;
          return b.interviewScore - a.interviewScore;
        });

        setCandidates(normalized);
      } catch (e) {
        console.error("AIInterviews fetch error:", e);
        setCandidates([]);
      }
    };
    fetchApps();
  }, [jobId, job]);

  return (
    <div>
      <AIInterviewJobHeader
        jobTitle={jobTitle || (jobId ? `Job ${jobId}` : "Backend Developer")}
        jobId={job?.id ?? jobId}
        invitedCount={candidates.length}
        mode="Asynchronous AI"
      />

      <div className="mt-6">
        {/* <AIInterviewFilters /> */}
        <div className="mt-6">
          <Card className="p-4">
            <AIInterviewOverview candidates={candidates} />

            <div className="mt-6">
              <CandidateInterviewList candidates={candidates} onSelect={setSelected} />
            </div>
          </Card>
        </div>
      </div>

      {selected && (
        <CandidateInterviewDetail candidate={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
};

export default AIInterviews;