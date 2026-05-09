import { useEffect, useState } from "react";
import { supabase } from "@/supabaseClient";
import ReportsJobHeader from "@/components/Reports/ReportsJobHeader";
import ReportsSummary from "@/components/Reports/ReportsSummary.tsx";
import TopCandidates from "@/components/Reports/TopCandidates.tsx";
import CandidatesTable from "@/components/Reports/CandidatesTable.tsx";
import { Card } from "@/components/ui/card";
import ReportsCharts from "@/components/Reports/ReportsCharts";

const toNum = (v: any): number | null => {
  const n = parseFloat(v);
  return isNaN(n) ? null : n;
};


const Reports = ({ jobId, job }: { jobId?: string; job?: any } = {}) => {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [rejectedCount, setRejectedCount] = useState(0);
  const [jobTitle, setJobTitle] = useState<string>(job?.title || job?.job_title || "");
  const [loading, setLoading] = useState(false);

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
      const id = job?.id ?? jobId;
      if (!id) return;
      setLoading(true);
      try {
        // Fetch INTERVIEW_GRADED applications for this job
        const { data: jobApps, error: jobAppsError } = await supabase
          .from("job_applications")
          .select("*")
          .eq("job_id", id)
          .eq("status", "INTERVIEW_GRADED");

        if (jobAppsError) throw jobAppsError;

        // Fetch count of REJECTED candidates for this job
        const { count: rejCount } = await supabase
          .from("job_applications")
          .select("id", { count: "exact", head: true })
          .eq("job_id", id)
          .eq("status", "REJECTED");
        setRejectedCount(rejCount ?? 0);

        if (!jobApps || jobApps.length === 0) {
          setCandidates([]);
          setLoading(false);
          return;
        }

        // Fetch applicant profiles for name/email
        const applicantIds = jobApps.map((a: any) => a.applicant_id).filter(Boolean);
        const { data: profiles } = await supabase
          .from("applications")
          .select("id, name, email, metadata")
          .in("id", applicantIds);

        const profileMap = new Map((profiles || []).map((p: any) => [p.id, p]));

        const normalized = jobApps.map((a: any) => {
          const profile = profileMap.get(a.applicant_id) || null;
          const metadata = profile?.metadata || {};
          const resumeScore = toNum(a.resume_score);
          const assessmentScore = toNum(a.assessment_score);
          const interviewScore = toNum(a.interview_score);
          return {
            id: a.id,
            applicant_id: a.applicant_id,
            name: profile?.name || metadata?.name || "Unknown",
            email: profile?.email || metadata?.email || "",
            resumeScore,
            assessmentScore,
            interviewScore,
            status: a.status,
            isShortlisted: interviewScore !== null && interviewScore >= 80,
          };
        });

        // Sort by interviewScore descending (nulls last)
        normalized.sort((a, b) => {
          if (a.interviewScore === null && b.interviewScore === null) return 0;
          if (a.interviewScore === null) return 1;
          if (b.interviewScore === null) return -1;
          return b.interviewScore - a.interviewScore;
        });

        // Mark top 2 among shortlisted
        let topCount = 0;
        const withTop = normalized.map((c) => {
          if (c.isShortlisted && topCount < 2) {
            topCount++;
            return { ...c, isTopCandidate: true };
          }
          return { ...c, isTopCandidate: false };
        });

        setCandidates(withTop);
      } catch (e) {
        console.error("Reports fetch error:", e);
        setCandidates([]);
      } finally {
        setLoading(false);
      }
    };
    fetchApps();
  }, [jobId, job]);

  const topCandidates = candidates.filter((c) => c.isTopCandidate);

  return (
    <div>
      <ReportsJobHeader
        jobTitle={jobTitle || (jobId ? `Job ${jobId}` : "—")}
        jobId={job?.id ?? jobId}
        totalEvaluated={candidates.length}
        topCandidates={topCandidates}
      />

      {loading && <p className="mt-4 text-sm text-muted-foreground">Loading report…</p>}

      {!loading && candidates.length === 0 && (
        <p className="mt-6 text-sm text-muted-foreground">No INTERVIEW_GRADED candidates found for this job.</p>
      )}

      {!loading && candidates.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          <div className="lg:col-span-2">
            <Card className="p-4 mb-6">
              <ReportsSummary candidates={candidates} rejectedCount={rejectedCount} />
            </Card>

            <Card className="p-4 mb-6">
              <TopCandidates candidates={topCandidates} />
            </Card>

            <Card className="p-4">
              <CandidatesTable candidates={candidates} />
            </Card>
          </div>

          <div>
            <Card className="p-4">
              <h3 className="text-lg font-semibold">Final Evaluation Graphs</h3>
              <div className="mt-4 text-sm text-muted-foreground">
                <ReportsCharts candidates={candidates} rejectedCount={rejectedCount} />
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

export default Reports;
