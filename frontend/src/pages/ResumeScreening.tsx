import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import JobHeader from "@/components/ResumeScreening/JobHeader";
import ScreeningOverview from "@/components/ResumeScreening/ScreeningOverview";
import FiltersPanel from "@/components/ResumeScreening/FiltersPanel";
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
  const [candidates] = useState(mockCandidates);
  const [searchParams] = useSearchParams();
  const jobId = propJobId ?? searchParams.get("jobId") ?? undefined;
  const [selected, setSelected] = useState<any | null>(null);
  const title = job?.title ?? (jobId ? `Job ${jobId}` : "Backend Developer");

  return (
    <div>
      <JobHeader jobTitle={`${title}${jobId && !job?.title ? ` (${jobId})` : ""}`} applicationsCount={candidates.length} />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
        <div className="lg:col-span-1">
          <FiltersPanel />
        </div>

        <div className="lg:col-span-3">
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
