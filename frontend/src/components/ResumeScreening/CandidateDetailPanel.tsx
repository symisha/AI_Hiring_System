import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const parseJsonSafely = (text: string) => {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
};

const parseMarkdownJsonBlocks = (text: string) => {
  const blocks = [...text.matchAll(/```json\s*([\s\S]*?)\s*```/gi)].map((m) => m[1].trim());
  if (!blocks.length) return null;

  const parsedBlocks = blocks
    .map((block) => parseJsonSafely(block))
    .filter((item) => item && typeof item === "object");

  if (!parsedBlocks.length) return null;
  if (parsedBlocks.length === 1) return parsedBlocks[0];

  return parsedBlocks.reduce((acc, curr) => ({ ...acc, ...curr }), {});
};

const parseInlineSectionJson = (text: string) => {
  const objects: any[] = [];
  let depth = 0;
  let start = -1;

  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];

    if (ch === "{") {
      if (depth === 0) start = i;
      depth += 1;
    } else if (ch === "}") {
      depth -= 1;
      if (depth === 0 && start !== -1) {
        const candidate = text.slice(start, i + 1);
        const parsed = parseJsonSafely(candidate);
        if (parsed && typeof parsed === "object") {
          objects.push(parsed);
        }
        start = -1;
      }
    }
  }

  if (!objects.length) return null;
  if (objects.length === 1) return objects[0];
  return objects.reduce((acc, curr) => ({ ...acc, ...curr }), {});
};

const parseEvaluation = (evalData: any) => {
  if (!evalData) return { parsed: null, rawText: null };

  if (typeof evalData === "object" && !Array.isArray(evalData)) {
    const raw = typeof evalData.raw === "string" ? evalData.raw : null;
    const fromRaw = raw ? parseEvaluation(raw).parsed : null;
    const merged = { ...fromRaw, ...evalData };
    delete merged.raw;
    return {
      parsed: Object.keys(merged).length ? merged : fromRaw,
      rawText: raw,
    };
  }

  if (typeof evalData === "string") {
    const trimmed = evalData.trim();
    const direct = parseJsonSafely(trimmed);
    if (direct) return { parsed: direct, rawText: trimmed };

    const blockParsed = parseMarkdownJsonBlocks(trimmed);
    if (blockParsed) return { parsed: blockParsed, rawText: trimmed };

    const jsonLikeSliceMatch = trimmed.match(/\{[\s\S]*\}/);
    if (jsonLikeSliceMatch) {
      const parsedSlice = parseJsonSafely(jsonLikeSliceMatch[0]);
      if (parsedSlice) return { parsed: parsedSlice, rawText: trimmed };
    }

    const mergedInline = parseInlineSectionJson(trimmed);
    if (mergedInline) return { parsed: mergedInline, rawText: trimmed };

    return { parsed: null, rawText: trimmed };
  }

  return { parsed: null, rawText: null };
};

const CandidateDetailPanel = ({ candidate, onClose }: any) => {
  const { parsed: evaluation, rawText } = parseEvaluation(candidate.resumeEvaluation);
  const displayStatus = candidate.reviewStatus || candidate.status || "N/A";
  const overallFitScore =
    evaluation?.overall_fit_score ?? candidate.resumeEvaluation?.overall_fit_score ?? candidate.aiScore ?? "N/A";
  
  return (
    <div className="fixed right-6 top-12 w-[900px] h-[80vh] bg-card rounded-2xl shadow-lg overflow-auto p-4">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-semibold">{candidate.name}</h3>
          <p className="text-sm text-muted-foreground">{candidate.email} • Applied: {candidate.appliedDate}</p>
        </div>

        <div className="flex gap-2">
          <Button onClick={() => alert('Shortlisted')}>Shortlist</Button>
          <Button onClick={() => alert('Rejected')} className="bg-red-600 text-white">Reject</Button>
          <Button onClick={onClose} className="bg-gray-200 text-black">Close</Button>
        </div>
      </div>

      <div className="space-y-4">
        {/* AI Analysis Score */}
        <Card className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50">
          <h4 className="font-semibold mb-3 text-indigo-600">AI Resume Evaluation</h4>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Overall Score:</span>
              <div className="font-bold text-lg text-indigo-600 mt-1">{overallFitScore}</div>
            </div>
            <div>
              <span className="text-muted-foreground">Status:</span>
              <div className={`font-bold text-lg mt-1 ${displayStatus === 'Shortlisted' || displayStatus === 'INTERVIEW_SCHEDULED' || displayStatus === 'ASSESSMENT_PENDING' ? 'text-green-600' : 'text-red-600'}`}>
                {displayStatus}
              </div>
            </div>
            <div>
              <span className="text-muted-foreground">Application Date:</span>
              <div className="text-yellow-600 font-semibold mt-1 text-sm">{candidate.appliedDate}</div>
            </div>
          </div>
        </Card>

        {/* Education Match */}
        {evaluation?.education && (
          <Card className="p-4">
            <h5 className="font-semibold mb-2">Education</h5>
            <div className="text-sm space-y-2">
              <div>
                <span className="text-muted-foreground">Required:</span> {evaluation.education.required}
              </div>
              <div>
                <span className="text-muted-foreground">Candidate:</span> {evaluation.education.candidate}
              </div>
              <div>
                <span className={`font-medium ${evaluation.education.match === 'yes' ? 'text-green-600' : 'text-red-600'}`}>
                  Match: {evaluation.education.match}
                </span>
              </div>
            </div>
          </Card>
        )}

        {/* Skills Match */}
        {evaluation?.skills && (
          <Card className="p-4">
            <h5 className="font-semibold mb-3">Skills Analysis</h5>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-xs font-semibold text-muted-foreground mb-1">REQUIRED SKILLS</p>
                <ul className="space-y-1">
                  {(evaluation.skills.required || []).map((s: string, i: number) => (
                    <li key={i} className="text-xs">• {s}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-muted-foreground mb-1">CANDIDATE SKILLS</p>
                <ul className="space-y-1">
                  {(evaluation.skills.candidate || []).map((s: string, i: number) => (
                    <li key={i} className="text-xs">• {s}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-green-600 mb-1">MATCHED</p>
                <ul className="space-y-1">
                  {(evaluation.skills.match || []).map((s: string, i: number) => (
                    <li key={i} className="text-xs text-green-700">✓ {s}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-red-600 mb-1">SKILL GAPS</p>
                <ul className="space-y-1">
                  {(evaluation.skills.gap || []).map((s: string, i: number) => (
                    <li key={i} className="text-xs text-red-700">✗ {s}</li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>
        )}

        {/* Projects */}
        {evaluation?.projects && evaluation.projects.length > 0 && (
          <Card className="p-4">
            <h5 className="font-semibold mb-3">Projects</h5>
            <div className="space-y-3">
              {evaluation.projects.map((p: any, i: number) => (
                <div key={i} className="border-l-2 border-indigo-300 pl-3 pb-2">
                  <p className="font-medium text-sm">{p.title}</p>
                  <p className="text-xs text-muted-foreground">Tools: {p.tools_methods?.join(', ') || 'N/A'}</p>
                  <p className={`text-xs font-semibold mt-1 ${p.relevance_to_JD === 'high' ? 'text-green-600' : p.relevance_to_JD === 'medium' ? 'text-yellow-600' : 'text-red-600'}`}>
                    Relevance: {p.relevance_to_JD}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Experience */}
        {evaluation?.experience && evaluation.experience.length > 0 && (
          <Card className="p-4">
            <h5 className="font-semibold mb-3">Work Experience</h5>
            <div className="space-y-2 text-sm">
              {evaluation.experience.map((exp: any, i: number) => (
                <div key={i} className="border-b pb-2 last:border-b-0">
                  <p className="font-medium">{exp.title || 'N/A'}</p>
                  <p className="text-xs text-muted-foreground">
                    {exp.start_date} - {exp.end_date || 'Present'} ({exp.duration_years} years)
                  </p>
                  <p className={`text-xs font-semibold ${exp.domain_relevance === 'relevant' ? 'text-green-600' : 'text-yellow-600'}`}>
                    {exp.domain_relevance}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Strengths & Weaknesses */}
        <div className="grid grid-cols-2 gap-4">
          {evaluation?.strengths && (
            <Card className="p-4 border-l-4 border-green-400">
              <h5 className="font-semibold mb-2 text-green-700">Strengths</h5>
              <ul className="text-xs space-y-1">
                {evaluation.strengths.map((s: string, i: number) => (
                  <li key={i} className="text-green-700">✓ {s}</li>
                ))}
              </ul>
            </Card>
          )}
          {evaluation?.weaknesses && (
            <Card className="p-4 border-l-4 border-red-400">
              <h5 className="font-semibold mb-2 text-red-700">Weaknesses</h5>
              <ul className="text-xs space-y-1">
                {evaluation.weaknesses.map((w: string, i: number) => (
                  <li key={i} className="text-red-700">✗ {w}</li>
                ))}
              </ul>
            </Card>
          )}
        </div>

        {!evaluation && rawText && (
          <Card className="p-4">
            <h5 className="font-semibold mb-2">Resume Evaluation (Raw)</h5>
            <pre className="text-xs whitespace-pre-wrap break-words bg-muted p-3 rounded-md">{rawText}</pre>
          </Card>
        )}

        {!evaluation && !rawText && (
          <Card className="p-4">
            <h5 className="font-semibold mb-2">Resume Evaluation</h5>
            <p className="text-sm text-muted-foreground">No resume evaluation available for this candidate.</p>
          </Card>
        )}
      </div>
    </div>
  );
};

export default CandidateDetailPanel;