#yet to connect database to the service for json file 
#yet to add s-t-text for the jd generation
#some logical errors, see json output to deliver 
import json

def ask(question):
    return input(f"{question}\n> ").strip()

def ask_choice(question, choices):
    print(question)
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    while True:
        try:
            selection = int(input("> "))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
        except ValueError:
            pass
        print("Invalid choice. Try again.")

def ask_multiple(question, choices):
    print(question)
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    print("Enter numbers separated by commas (e.g. 1,3,5)")
    selected = input("> ")
    indices = selected.split(",")
    return [choices[int(i.strip()) - 1] for i in indices if i.strip().isdigit()]

def questionnaire():
    data = {}

    # SECTION 1: ROLE IDENTITY
    data["job_title"] = ask("Job title:")
    data["alternate_titles"] = ask("Alternative job titles (comma separated):")
    data["department"] = ask("Department / Team:")
    data["industry"] = ask_choice(
        "Industry domain:",
        ["FinTech", "HealthTech", "EdTech", "E-commerce", "SaaS", "AI/ML", "Gaming", "Telecom", "Other"]
    )
    data["employment_type"] = ask_choice(
        "Employment type:",
        ["Full-time", "Part-time", "Contract", "Internship"]
    )
    data["work_model"] = ask_choice(
        "Work model:",
        ["Onsite", "Hybrid", "Remote"]
    )
    data["seniority"] = ask_choice(
        "Seniority level:",
        ["Intern", "Junior", "Mid", "Senior", "Lead", "Principal", "Manager"]
    )

    # SECTION 2: ROLE OBJECTIVE
    data["role_problem"] = ask("What problem does this role solve?")
    data["success_6_months"] = ask("What does success look like after 6 months?")
    data["success_12_months"] = ask("What does success look like after 12 months?")

    # SECTION 3: RESPONSIBILITIES
    data["responsibilities"] = []
    print("Enter top responsibilities (type 'done' to finish):")
    while True:
        r = input("> ")
        if r.lower() == "done":
            break
        data["responsibilities"].append(r)

    # SECTION 4: TECHNICAL SKILLS
    data["languages"] = ask_multiple(
        "Required programming languages:",
        ["Python", "Java", "C++", "JavaScript", "TypeScript", "Go", "Rust", "SQL", "Other"]
    )
    data["frameworks"] = ask("Required frameworks/libraries:")
    data["databases"] = ask_multiple(
        "Databases used:",
        ["MySQL", "PostgreSQL", "MongoDB", "Redis", "DynamoDB"]
    )
    data["cloud"] = ask_multiple(
        "Cloud platforms:",
        ["AWS", "Azure", "GCP", "None"]
    )

    # SECTION 5: DOMAIN KNOWLEDGE
    data["domain_expertise"] = ask_choice("Requires domain expertise?", ["Yes", "No"])
    if data["domain_expertise"] == "Yes":
        data["domains"] = ask_multiple(
            "Select domains:",
            ["AI/ML", "Data Engineering", "Cybersecurity", "Cloud", "Mobile", "Web", "Blockchain"]
        )

    # SECTION 6: EXPERIENCE
    data["min_experience_years"] = ask("Minimum years of experience:")
    data["education_required"] = ask_choice(
        "Required education:",
        ["None", "Bachelor", "Master", "PhD"]
    )

    # SECTION 7: PROBLEM SOLVING
    data["problem_solving_level"] = ask_choice(
        "Problem-solving complexity:",
        ["Low", "Medium", "High"]
    )

    # SECTION 8: SOFT SKILLS
    data["soft_skills"] = ask_multiple(
        "Important soft skills:",
        ["Communication", "Teamwork", "Leadership", "Autonomy", "Adaptability"]
    )

    # SECTION 9: DECISION MAKING
    data["decision_authority"] = ask_choice(
        "Decision-making authority:",
        ["Low", "Medium", "High"]
    )

    # SECTION 10: PERFORMANCE METRICS
    data["performance_metrics"] = ask("How will performance be measured?")

    # SECTION 11: DEALBREAKERS
    data["must_haves"] = ask("Absolute must-haves:")
    data["dealbreakers"] = ask("Absolute dealbreakers:")

    # SECTION 12: GROWTH
    data["growth_path"] = ask_choice(
        "Growth path:",
        ["Technical", "Managerial", "Hybrid"]
    )

    # SECTION 13: INTERVIEW PREFERENCES
    data["interview_focus"] = ask_multiple(
        "Interview focus:",
        ["Coding", "System Design", "Case Study", "Behavioral", "Research"]
    )
    data["interview_difficulty"] = ask_choice(
        "Interview difficulty:",
        ["Easy", "Medium", "Hard", "Adaptive"]
    )

    return data


if __name__ == "__main__":
    responses = questionnaire()

    with open("job_description_questionnaire.json", "w") as f:
        json.dump(responses, f, indent=4)

    print("\n✅ Questionnaire completed.")
    print("📁 Saved as job_description_questionnaire.json")
