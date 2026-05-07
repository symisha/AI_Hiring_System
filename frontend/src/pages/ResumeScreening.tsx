import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { supabase } from "@/supabaseClient";
import JobHeader from "@/components/ResumeScreening/JobHeader";
import ScreeningOverview from "@/components/ResumeScreening/ScreeningOverview";

import CandidateList from "@/components/ResumeScreening/CandidateList";
import CandidateDetailPanel from "@/components/ResumeScreening/CandidateDetailPanel";
import { Card } from "@/components/ui/card";

const SHORTLIST_THRESHOLD = 75;

const toNumberOrNull = (value: unknown): number | null => {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
};

const ResumeScreening = ({ jobId: propJobId, job }: { jobId?: string; job?: any } = {}) => {
  const [candidates, setCandidates] = useState<any[]>([]);
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
      if (!jobId) {
        setCandidates([]);
        return;
      }
      try {
        const { data: jobApps, error: jobAppsError } = await supabase
          .from("job_applications")
          .select("*")
          .eq("job_id", jobId)
          .order("submitted_at", { ascending: false, nullsFirst: false });

        if (jobAppsError) throw jobAppsError;

        const { data: applications, error: applicationsError } = await supabase
          .from("applications")
          .select("id, name, email, metadata")
          .eq("job_id", jobId);

        if (applicationsError) throw applicationsError;

        const applicationsById = new Map(
          (applications || []).map((app: any) => [app.id, app])
        );

        const normalized = (jobApps || []).map((a: any) => {
          const application = applicationsById.get(a.applicant_id) || null;
          const metadata = application?.metadata || {};
          const score = toNumberOrNull(a.resume_score);
          return {
            id: a.id || a.applicant_id,
            name: application?.name || metadata.name || a.name || a.applicant_name || "Unknown",
            email: application?.email || metadata.email || a.applicant_email || a.email || "",
            appliedDate: a.submitted_at || a.created_at || null,
            experience: metadata.experiences?.[0]?.years || a.experience || null,
            education: a.education || null,
            skills: Array.isArray(metadata.skills)
              ? metadata.skills
              : Array.isArray(a.skills)
                ? a.skills
                : [],
            aiScore: score,
            status: score !== null && score > SHORTLIST_THRESHOLD ? "Shortlisted" : "Rejected",
            reviewStatus: a.status || null,
            resume: a.resume_url || a.resume_path || null,
            reasons: a.reasons || [],
            resumeEvaluation: a.resume_evaluation || null,
          };
        }).filter((c: any) => c.aiScore !== null);

        normalized.sort((a, b) => {
          if (a.aiScore === null && b.aiScore === null) return 0;
          if (a.aiScore === null) return 1;
          if (b.aiScore === null) return -1;
          return b.aiScore - a.aiScore;
        });

        setCandidates(normalized);
      } catch (e) {
        console.error("ResumeScreening fetch error:", e);
        setCandidates([]);
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