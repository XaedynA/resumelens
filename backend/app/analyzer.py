"""Explainable, local-first resume/job comparison (no third-party API calls)."""
import re
from collections import Counter

SKILLS = {
 "Python": ["python"], "JavaScript": ["javascript", "js"], "TypeScript": ["typescript"],
 "React": ["react", "react.js"], "Node.js": ["node.js", "nodejs"],
 "SQL": ["sql", "mysql", "sqlite"], "PostgreSQL": ["postgresql", "postgres"],
 "AWS": ["aws", "amazon web services"], "Azure": ["azure", "microsoft azure"],
 "Docker": ["docker", "containerization"], "Kubernetes": ["kubernetes", "k8s"],
 "Git": ["git", "version control"], "GitHub Actions": ["github actions"],
 "FastAPI": ["fastapi"], "Django": ["django"], "Flask": ["flask"],
 "REST APIs": ["rest api", "restful", "api development", "backend api", "web api"],
 "Linux": ["linux", "ubuntu"], "Networking": ["networking", "tcp/ip", "network protocols"],
 "Cybersecurity": ["cybersecurity", "cyber security", "information security"],
 "SIEM": ["siem", "security information and event management"], "Splunk": ["splunk"],
 "Pandas": ["pandas"], "Excel": ["excel", "spreadsheets"], "Power BI": ["power bi"],
 "Tableau": ["tableau"], "Machine Learning": ["machine learning", "ml models"],
 "PyTorch": ["pytorch"], "Testing": ["pytest", "unit testing", "automated testing", "test automation", "selenium"],
 "CI/CD": ["ci/cd", "continuous integration", "continuous deployment", "github actions"],
 "Communication": ["communication", "communicate", "written and verbal", "stakeholder updates"],
 "Project Management": ["project management", "project coordination", "agile", "scrum"],
 "C#": ["c#"], "C++": ["c++"], "Java": ["java"], "HTML": ["html"], "CSS": ["css"],
 "Customer Support": ["customer support", "customer service", "technical support", "help desk", "troubleshooting"],
 "Data Analysis": ["data analysis", "data analytics", "analyzing data", "data analyst"],
 "Security+": ["security+", "comptia security plus", "comptia security+"],
 "CompTIA A+": ["comptia a+", "a+ certification"],
 "Network+": ["network+", "comptia network plus"],
 "Active Directory": ["active directory", "microsoft entra", "entra id"],
 "Incident Response": ["incident response", "incident handling", "security incidents"],
 "Threat Detection": ["threat detection", "intrusion detection", "suspicious traffic", "security monitoring"],
 "Documentation": ["documentation", "technical writing", "documenting procedures"],
 "Attention to Detail": ["attention to detail", "detail-oriented", "quality assurance"],
}
STOPWORDS = set("the a an and or for with in on at to of as is are be will can our your you we this that by from have has using experience years year plus ability strong good knowledge skills work working team role job required preferred candidate must able demonstrated including within their they them about an into also all any who what where when through per position provide performing".split())
CERTS = {"Security+", "CompTIA A+", "Network+"}

def contains_term(text, term):
    return bool(re.search(r"(?<![a-zA-Z0-9+#])" + re.escape(term.lower()) + r"(?![a-zA-Z0-9+#])", text.lower()))

def extract_skills(text):
    return sorted(name for name, aliases in SKILLS.items() if any(contains_term(text, alias) for alias in aliases))

def keywords(text):
    return Counter(w for w in re.findall(r"[a-z][a-z0-9-]{2,}", text.lower()) if w not in STOPWORDS)

def snippets(text):
    return [s.strip() for s in re.split(r"[\n\r]+|(?<=[.!?])\s+(?=[A-Z])", text) if s.strip()]

def evidence(text, skill):
    aliases = SKILLS[skill]
    for line in snippets(text):
        if any(contains_term(line, alias) for alias in aliases):
            return line[:260]
    return None

def requirements(job):
    result = []
    lines = snippets(job)
    for skill in extract_skills(job):
        supporting = next((line for line in lines if any(contains_term(line, a) for a in SKILLS[skill])), "")
        preferred = bool(re.search(r"\b(preferred|nice to have|bonus|plus|desirable)\b", supporting, re.I))
        result.append({"skill": skill, "priority": "preferred" if preferred else "core", "job_evidence": supporting[:260]})
    return result

def analyze(resume, job):
    if not resume.strip() or not job.strip():
        raise ValueError("Resume and job description must not be empty")
    reqs = requirements(job)
    found = set(extract_skills(resume))
    matched = sorted(r["skill"] for r in reqs if r["skill"] in found)
    missing = sorted(r["skill"] for r in reqs if r["skill"] not in found)
    for r in reqs:
        r["status"] = "mentioned" if r["skill"] in found else "not_found"
        r["resume_evidence"] = evidence(resume, r["skill"]) if r["skill"] in found else None
    total = sum(2 if r["priority"] == "core" else 1 for r in reqs)
    hit = sum((2 if r["priority"] == "core" else 1) for r in reqs if r["status"] == "mentioned")
    # Never present a numeric score based on one generic skill or no meaningful requirements.
    score = round(100 * hit / total) if len(reqs) >= 3 else None
    resume_words, job_words = keywords(resume), keywords(job)
    overlap = sorted(set(resume_words) & set(job_words))
    suggestions = []
    if missing:
        suggestions.append("Review these job requirements. Add them only if you can truthfully demonstrate them: " + ", ".join(missing[:8]) + ".")
    if len(resume.split()) < 120:
        suggestions.append("Add specific project or work accomplishments with context and results, where available.")
    if not re.search(r"\b(built|developed|created|improved|automated|implemented|analyzed|led|resolved)\b", resume, re.I):
        suggestions.append("Use action verbs in experience bullets and describe what changed because of your work.")
    if not re.search(r"\b\d+(?:%|\+)?\b", resume):
        suggestions.append("Quantify your results where accurate; never invent metrics.")
    if not suggestions:
        suggestions.append("For each relevant requirement, explain how and where you used the skill, with a specific outcome.")
    suggestions.append("A skill mention is not proof of proficiency. Review all recommendations before editing your resume.")
    return {
        "score": score, "score_label": "Recognized requirement coverage" if score is not None else "Not enough recognized requirements for a reliable percentage",
        "matched_skills": matched, "missing_skills": missing, "resume_skills": sorted(found),
        "job_skills": sorted(r["skill"] for r in reqs), "requirements": reqs,
        "keyword_matches": overlap[:20], "suggestions": suggestions,
        "coverage": {"matched": len(matched), "recognized": len(reqs)},
        "method": "Local, explainable dictionary-based requirement coverage. Not semantic AI, an ATS score, proof of qualification, or a hiring prediction."
    }
