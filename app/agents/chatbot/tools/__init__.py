from app.agents.chatbot.tools.analysis_tools import (
    get_all_analyses,
    get_analysis_details,
    search_analyses_by_candidate,
    get_top_candidates,
)
from app.agents.chatbot.tools.resume_tools import get_all_resumes, get_resume_content
from app.agents.chatbot.tools.job_tools import (
    get_all_jobs,
    get_job_details,
    get_analyses_for_job,
)

all_tools = [
    get_all_analyses,
    get_analysis_details,
    search_analyses_by_candidate,
    get_top_candidates,
    get_all_resumes,
    get_resume_content,
    get_all_jobs,
    get_job_details,
    get_analyses_for_job,
]
