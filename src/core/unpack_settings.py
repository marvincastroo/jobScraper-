import settings

USER_DESCRIPTION = getattr(settings, 'USER_DESCRIPTION', None)
if USER_DESCRIPTION is None:
    raise ValueError(
        "USER_DESCRIPTION variable is not initialized in settings.py. A basic user description is necessary"
        "for the tool to work.")
USER_NAME = getattr(settings, 'USER_NAME', "")
USER_EDUCATION = getattr(settings, 'USER_EDUCATION', "")
USER_SKILLS = getattr(settings, 'USER_SKILLS', "")
USER_EXPERIENCE = getattr(settings, 'USER_EXPERIENCE', "")
USER_PROJECTS = getattr(settings, 'USER_PROJECTS', "")
USER_LANGUAGES = getattr(settings, 'USER_LANGUAGES', "")
USER_CERTIFICATIONS = getattr(settings, 'USER_CERTIFICATIONS', "")

JOB_FINDINGS_FILTER = getattr(settings, 'JOB_FINDINGS_FILTER', [])
JOB_TYPE_TARGETS = getattr(settings, 'JOB_TYPE_TARGETS', [])
FILTER_JOBS_KEYWORDS = getattr(settings, 'FILTER_JOBS_KEYWORDS', [])
FILTER_COMPANIES = getattr(settings, 'FILTER_COMPANIES', [])