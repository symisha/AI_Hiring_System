const ReportsSummary = ({ candidates, rejectedCount = 0 }: any) => {
  const total = candidates.length;
  const shortlisted = candidates.filter((c: any) => c.isShortlisted).length;
  const topCandidates = candidates.filter((c: any) => c.isTopCandidate).length;
  const withAssessment = candidates.filter((c: any) => c.assessmentScore != null).length;
  const withInterview = candidates.filter((c: any) => c.interviewScore != null).length;

  return (
    <div>
      <h3 className="text-lg font-semibold">Overall Summary</h3>
      <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>Interview graded candidates: <strong>{total}</strong></div>
        <div>Shortlisted (score ≥ 80): <strong>{shortlisted}</strong></div>
        <div>Assessments completed: <strong>{withAssessment}</strong></div>
        <div>Interviews completed: <strong>{withInterview}</strong></div>
        <div>Top candidates: <strong>{topCandidates}</strong></div>
        <div>Rejected: <strong>{rejectedCount}</strong></div>
      </div>
    </div>
  );
};

export default ReportsSummary;
