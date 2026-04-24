export enum AppStatus {
    RESUME_RECEIVED = "RESUME_RECEIVED",
    RESUME_GRADED = "RESUME_GRADED",
    ASSESSMENT_PENDING = "ASSESSMENT_PENDING",
    ASSESSMENT_GRADED = "ASSESSMENT_GRADED",
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED",
    REJECTED = "REJECTED"
}

export interface SolutionEntry {
    question_id: string;
    code: string;
}

export interface TestSubmissionPayload {
    token: string;
    solutions: SolutionEntry[];
}