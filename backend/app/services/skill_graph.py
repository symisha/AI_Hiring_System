from app.database.db_connection import supabase

skill_json = {
  "core_concepts": [
    "algorithms",
    "data structures",
    "complexity analysis",
    "recursion",
    "dynamic programming",
    "graph theory",
    "sorting",
    "searching",
    "hashing",
    "memory management",
    "concurrency",
    "parallelism",
    "operating systems",
    "networking fundamentals",
    "computer architecture",
    "compilers",
    "automata theory",
    "boolean logic",
    "bit manipulation",
    "object-oriented programming",
    "functional programming",
    "design patterns",
    "event-driven programming",
    "type systems",
    "distributed computing"
  ],
  "programming_languages": [
    "python",
    "javascript",
    "typescript",
    "java",
    "c",
    "c++",
    "c#",
    "go",
    "rust",
    "scala",
    "kotlin",
    "swift",
    "r",
    "sql",
    "bash",
    "ruby",
    "php",
    "dart",
    "matlab",
    "julia",
    "elixir",
    "haskell",
    "lua",
    "assembly",
    "solidity"
  ],
  "tools_and_technologies": [
    "git",
    "docker",
    "linux",
    "rest apis",
    "graphql",
    "webpack",
    "npm",
    "postman",
    "vs code",
    "jupyter notebooks",
    "redis",
    "nginx",
    "kafka",
    "rabbitmq",
    "elasticsearch",
    "grpc",
    "websockets",
    "oauth",
    "openapi",
    "terraform",
    "ansible",
    "makefile",
    "vim",
    "jira",
    "figma"
  ],
  "data_skills": [
    "sql querying",
    "data wrangling",
    "data visualization",
    "statistical analysis",
    "machine learning",
    "deep learning",
    "natural language processing",
    "computer vision",
    "feature engineering",
    "model evaluation",
    "data pipelines",
    "etl",
    "data modeling",
    "exploratory data analysis",
    "time series analysis",
    "regression",
    "classification",
    "clustering",
    "reinforcement learning",
    "dimensionality reduction",
    "data warehousing",
    "big data",
    "spark",
    "pandas",
    "numpy"
  ],
  "system_and_design": [
    "system design",
    "microservices",
    "monolithic architecture",
    "api design",
    "database design",
    "caching",
    "load balancing",
    "scalability",
    "high availability",
    "fault tolerance",
    "event sourcing",
    "cqrs",
    "service mesh",
    "domain-driven design",
    "clean architecture",
    "mvc",
    "message queues",
    "rate limiting",
    "sharding",
    "replication",
    "cap theorem",
    "consistency models",
    "latency optimization",
    "cdn",
    "proxy design"
  ],
  "devops_and_cloud": [
    "aws",
    "azure",
    "google cloud",
    "kubernetes",
    "ci/cd",
    "infrastructure as code",
    "monitoring",
    "logging",
    "alerting",
    "serverless",
    "containers",
    "helm",
    "github actions",
    "jenkins",
    "cloud networking",
    "iam",
    "auto scaling",
    "blue-green deployment",
    "canary deployment",
    "site reliability engineering",
    "observability",
    "secrets management",
    "cloud storage",
    "cost optimization",
    "gitops"
  ],
  "testing_and_quality": [
    "unit testing",
    "integration testing",
    "end-to-end testing",
    "test-driven development",
    "behavior-driven development",
    "mocking",
    "code coverage",
    "regression testing",
    "performance testing",
    "load testing",
    "smoke testing",
    "static analysis",
    "linting",
    "code review",
    "fuzzing",
    "mutation testing",
    "accessibility testing",
    "api testing",
    "test automation",
    "debugging",
    "profiling",
    "chaos engineering",
    "contract testing",
    "snapshot testing",
    "quality metrics"
  ],
  "security": [
    "cryptography",
    "authentication",
    "authorization",
    "owasp",
    "penetration testing",
    "vulnerability assessment",
    "secure coding",
    "threat modeling",
    "sql injection",
    "xss",
    "csrf",
    "tls/ssl",
    "firewalls",
    "network security",
    "zero trust",
    "siem",
    "incident response",
    "identity management",
    "data encryption",
    "key management",
    "dependency auditing",
    "devsecops",
    "cloud security",
    "social engineering awareness",
    "compliance"
  ],
  "soft_skills": [
    "communication",
    "problem solving",
    "critical thinking",
    "collaboration",
    "time management",
    "adaptability",
    "leadership",
    "mentoring",
    "documentation",
    "attention to detail",
    "creativity",
    "ownership",
    "conflict resolution",
    "active listening",
    "presentation skills",
    "self-learning",
    "prioritization",
    "empathy",
    "cross-functional teamwork",
    "remote collaboration",
    "decision making",
    "resilience",
    "goal setting",
    "feedback receptivity",
    "analytical thinking"
  ],
  "business_and_product": [
    "agile methodology",
    "scrum",
    "kanban",
    "product thinking",
    "user research",
    "requirements gathering",
    "roadmap planning",
    "ux principles",
    "a/b testing",
    "kpi definition",
    "stakeholder management",
    "customer empathy",
    "mvp development",
    "market analysis",
    "data-driven decisions",
    "sprint planning",
    "backlog grooming",
    "okrs",
    "business intelligence",
    "sla management",
    "cost-benefit analysis",
    "technical writing",
    "risk assessment",
    "go-to-market strategy",
    "competitive analysis"
  ]
}

skill_lookup = {}

for category, skills in skill_json.items():
    for skill in skills:
        skill_lookup[skill] = category

import re

SYNONYMS = {
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "eda": "exploratory data analysis",
    "js": "javascript",
    "ts": "typescript"
}

def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s/+#.]', ' ', text)  # supports c++, c#, node.js
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def apply_synonyms(text):
    words = text.split()
    expanded = words.copy()

    for word in words:
        if word in SYNONYMS:
            expanded.append(SYNONYMS[word])

    return " ".join(expanded)


def match_skill(skill, text):
    pattern = r'\b' + re.escape(skill) + r'\b'
    return re.search(pattern, text) is not None


def score_skill(skill, text):
    return len(re.findall(r'\b' + re.escape(skill) + r'\b', text))

def extract_skills(jd_text, skill_lookup):
    text = normalize(jd_text)
    text = apply_synonyms(text)

    found_skills = {}

    # prioritize longer skills first
    sorted_skills = sorted(skill_lookup.items(), key=lambda x: -len(x[0]))

    for skill, category in sorted_skills:
        if match_skill(skill, text):
            found_skills[skill] = {
                "category": category,
                "score": score_skill(skill, text)
            }

    return found_skills

def format_job_metadata(job):
    m = job.get("job_metadata", {})

    def _flatten_to_strings(value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, tuple)):
            out = []
            for v in value:
                out.extend(_flatten_to_strings(v))
            return out
        return [str(value)]

    def clean_list(value):
        parts = []
        for s in _flatten_to_strings(value):
            s = str(s).strip()
            if s:
                parts.append(s)
        return " ".join(parts)

    def get_meta(*keys, default=""):
        for k in keys:
            if k in m and m.get(k) not in (None, "", [], {}):
                return m.get(k)
        return default

    # Support both "Key X" and "Key X:" styles (some jobposts include trailing colons)
    key_skills = get_meta(
        "Key Skills",
        "Key Skills:",
        "Skills",
        "Skills:",
        "Qualifications",
        "Qualifications:",
        default="",
    )
    key_responsibilities = get_meta(
        "Key Responsibilities",
        "Key Responsibilities:",
        "Responsibilities",
        "Responsibilities:",
        default=[],
    )
    required_qualifications = get_meta(
        "Required Qualifications",
        "Required Qualifications:",
        "Requirements",
        "Requirements:",
        default=[],
    )
    preferred_qualifications = get_meta(
        "Preferred Qualifications",
        "Preferred Qualifications:",
        default=[],
    )
    what_we_offer = get_meta(
        "What We Offer",
        "What We Offer:",
        default="",
    )

    return " ".join(
        [
            job.get("job_title", ""),
            clean_list(key_skills),
            clean_list(key_responsibilities),
            clean_list(required_qualifications),
            clean_list(preferred_qualifications),
            clean_list(what_we_offer),
        ]
    )

def fetch_job_details(job_id):
    response = supabase.table("jobs").select(
        "job_title, job_metadata, department, seniority"
    ).eq("id", job_id).execute()

    if response.data:
        return response.data[0]
    return None


def build_skill_map(job_id):
    job = fetch_job_details(job_id)

    if not job:
        print("No job found")
        return None

    jd_text = format_job_metadata(job)

    skill_map = extract_skills(jd_text, skill_lookup)

    return skill_map

#SKILLS GRAPH COMPLETED
#INTERVIEW STAGE NOW STARTING
def assign_stage(skill, data):
    category = data["category"]
    score = data["score"]

    # Behavioral always separate
    if category == "soft_skills":
        return "behavioral"

    # Core knowledge
    if category in ["core_concepts"]:
        return "core"

    # Data roles / backend / etc
    if category in ["data_skills", "programming_languages"]:
        if score >= 2:
            return "core"
        return "applied"

    # Tools always applied
    if category in ["tools_and_technologies", "devops_and_cloud"]:
        return "applied"

    # fallback
    return "background"

def build_interview_flow(skill_map):
    flow = {
        "background": [],
        "core": [],
        "applied": [],
        "behavioral": []
    }

    for skill, data in skill_map.items():
        stage = assign_stage(skill, data)
        flow[stage].append({
            "skill": skill,
            "score": data["score"]
        })

    # sort by importance (VERY IMPORTANT)
    for stage in flow:
        flow[stage] = sorted(
            flow[stage],
            key=lambda x: -x["score"]
        )

    return flow


if __name__ == "__main__":
    job_id = "4d9c7579-4844-4a06-bf5b-f3160694f296"
    skill_map = build_skill_map(job_id)
    print("=== Skill Map ===")
    print(skill_map)
    print("\n=== Interview Flow (by Stage) ===")
    interview_flow = build_interview_flow(skill_map)
    for stage, skills in interview_flow.items():
        print(f"\n{stage.upper()}:")
        for s in skills:
            print(f"  - {s['skill']} (score: {s['score']})")