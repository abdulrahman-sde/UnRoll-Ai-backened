from app.schemas.analysis import AnalysisResultSchema
from app.utils.ai import build_embedding_text
import json

# Sample AI Output matching the schema
sample_analysis = {
    "candidate_name": "John Doe",
    "contact": {
        "email": "john@example.com",
        "phone": "123-456-7890",
        "location": "New York, NY",
        "linkedin": "linkedin.com/in/johndoe",
        "github": "github.com/johndoe",
        "portfolio": "johndoe.com",
        "extraction_confidence": "HIGH"
    },
    "education": [
        {
            "degree": "BSc Computer Science",
            "institution": "MIT",
            "graduation_year": 2020,
            "gpa": 3.8
        }
    ],
    "total_experience_years": 4.5,
    "target_role": "Senior Software Engineer",
    "scores": {
        "overall": 85,
        "tech": 90,
        "experience": 80,
        "education": 85,
        "culture": 90
    },
    "score_justification": {
        "tech": "Strong React and Python skills.",
        "experience": "Solid 4 years in fintech.",
        "education": "Top tier university.",
        "culture": "Collaborative mindset."
    },
    "recommendation": "HIRE",
    "hire_recommendation": True,
    "summary": "John is a highly skilled engineer with a background in large-scale systems.",
    "shortlist_summary": "Top-tier candidate from MIT with strong React skills.",
    "key_vectors": ["React", "Python", "Large-scale systems"],
    "skills": [
        {"name": "React", "years": 4.0, "level": 90},
        {"name": "Python", "years": 4.5, "level": 85}
    ],
    "experience": [
        {
            "title": "Senior Engineer",
            "company": "TechFlow Systems",
            "start_year": 2020,
            "end_year": None,
            "duration_years": 4.0,
            "match_percentage": 95,
            "description": "Led a team of 5 to build a scalable dashboard."
        }
    ],
    "red_flags": [],
    "suggested_interview_questions": ["Tell me about a time you led a team."],
    "salary_estimate": {
        "min": 120000,
        "max": 150000,
        "currency": "USD",
        "confidence": "HIGH",
        "reasoning": "Based on market rates for Senior Engineers."
    },
    "culture_signals": {
        "positive": ["Team leader", "Open source contributor"],
        "negative": []
    },
    "extraction_status": {
        "personal_info": True,
        "education": True,
        "experience": True,
        "skills": True,
        "projects": True
    }
}

def verify():
    print("Testing Pydantic schema validation...")
    try:
        analysis_obj = AnalysisResultSchema(**sample_analysis)
        print("✅ Pydantic validation successful.")
        
        print("\nTesting build_embedding_text utility...")
        embedding_text = build_embedding_text(analysis_obj)
        print("Generated text preview:")
        print("-" * 20)
        print(embedding_text[:300] + "...")
        print("-" * 20)
        print("✅ Embedding text generation successful.")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    verify()
