# profile.py
# ─────────────────────────────────────────────────────────────────────────────
# YOUR PERSONAL PROFILE
# The AI uses this information to fill application forms automatically.
# ─────────────────────────────────────────────────────────────────────────────

import os

PROFILE = {
    # ── Basic Info ────────────────────────────────────────────────────────────
    "name":             "Shirshendu Sen",
    "email":            "shirshendusen7@gmail.com",
    "phone":            "+91 8972196139",
    "location":         "West Bengal, India",

    "linkedin_url":     "https://www.linkedin.com/in/shirshendu-sen-7253161aa/",
    "github_url":       "https://github.com/Shirshendu-sen",
    "portfolio_url":    "https://portfolio-shirshendu.web.app/",

    # Optional coding profiles
    "leetcode_url":     "",
    "codeforces_url":   "",
    "hackerrank_url":   "",

    # ── Resume ────────────────────────────────────────────────────────────────
    "resume_path": os.path.join(
        os.path.dirname(__file__),
        "resume",
        "Resume.pdf"
    ),

    # ── Work Experience ───────────────────────────────────────────────────────
    "experience_years":     1,
    "current_company":      "",
    "current_designation":  "Generative AI Intern",
    "current_ctc":          "",
    "expected_ctc":         "8 LPA",
    "notice_period":        "Immediate",

    # ── Skills ────────────────────────────────────────────────────────────────
    "primary_skills": [
        "Python",
        "Node.js",
        "React.js",
        "Next.js",
        "TypeScript",
        "REST APIs",
        "GenAI",
        "LangChain",
        "PostgreSQL",
        "Docker"
    ],

    "secondary_skills": [
        "Flask",
        "Express.js",
        "MongoDB",
        "Firebase",
        "AWS",
        "Azure",
        "GraphQL",
        "CI/CD",
        "GitHub Actions",
        "Linux",
        "PyTorch",
        "NLP",
        "Transformer Models",
        "RAG"
    ],

    # ── Education ─────────────────────────────────────────────────────────────
    "degree":           "M.Sc Computer Science",
    "college":          "University of Calcutta",
    "graduation_year":  2026,
    "percentage_cgpa":  "",

    # ── Job Preferences ───────────────────────────────────────────────────────
    "target_roles": [
        "Backend Engineer",
        "Python Developer",
        "Full Stack Developer",
        "Software Engineer",
        "AI Engineer",
        "GenAI Engineer",
        "Backend Developer",
    ],

    "preferred_locations": [
        "Remote",
        "Bangalore",
        "Hyderabad",
        "Kolkata",
        "Pune"
    ],

    "preferred_job_types": [
        "Full-time",
        "Internship",
        "Remote"
    ],

    "preferred_company_types": [
        "Startup",
        "Product Company",
        "AI Company",
        "SaaS"
    ],

    "work_mode":           "any",
    "remote_preference":   True,
    "open_to_internships": True,
    "min_salary_lpa":      6,

    # ── Company Filters ───────────────────────────────────────────────────────
    # Empty list = apply to all companies
    "blacklisted_companies": [],

    # ── Availability & Work Authorization ────────────────────────────────────
    "availability":                 "Immediate",
    "authorized_to_work_in_india": True,
    "visa_sponsorship_required":   False,
    "open_to_relocation":          True,

    # ── LinkedIn Headline ─────────────────────────────────────────────────────
    "linkedin_headline": (
        "Full Stack Developer | AI & GenAI Enthusiast | "
        "Python • Next.js • Node.js • LangChain"
    ),

    # ── Cover Letter Snippet ──────────────────────────────────────────────────
    "cover_letter_summary": (
        "I am a Full Stack and AI-focused developer with hands-on experience "
        "building scalable web applications, AI-powered systems, REST APIs, "
        "and cloud-deployed solutions using Python, Node.js, React, Next.js, "
        "and Generative AI technologies. I enjoy solving real-world problems "
        "through clean architecture, scalable backend systems, and modern AI "
        "integration."
    ),

    # ── Answers to Common Application Questions ───────────────────────────────
    "are_you_freshers":             True,
    "willing_to_relocate":          True,
    "have_own_laptop":              True,
    "disability":                   False,
    "gender":                       "Male",
    "nationality":                  "Indian",
}