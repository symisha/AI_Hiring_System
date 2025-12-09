const ReportsSummary = ({ candidates }: any) => {
  const total = candidates.length;
  const shortlisted = Math.round(total * 0.6);
  const assessmentsCompleted = candidates.filter((c:any)=>c.assessment!=null).length;
  const interviewsCompleted = candidates.filter((c:any)=>c.interview!=null).length;

  return (
    <div>
      <h3 className="text-lg font-semibold">Overall Summary</h3>
      <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>Total applications: <strong>{total}</strong></div>
        <div>Resumes shortlisted: <strong>{shortlisted}</strong></div>
        <div>Assessments completed: <strong>{assessmentsCompleted}</strong></div>
        <div>AI Interviews completed: <strong>{interviewsCompleted}</strong></div>
        <div>Final candidates considered: <strong>{Math.min(5, total)}</strong></div>
      </div>
    </div>
  );
};

export default ReportsSummary;
