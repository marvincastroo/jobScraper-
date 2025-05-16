from src.scrapers.linkedin_scraper import LinkedInScraper
from src.scrapers.workday_scraper import WorkdayScraper

def scraper_classifier(job_details):
    url = job_details['link']
    if url.startswith("https://www.linkedin.com/jobs/view/"):
        print(f"processing linkedin")
        scraper = LinkedInScraper(url)
        return scraper.parse()
    elif "myworkdayjobs.com" in url:
        print(f"processing workday")
        scraper = WorkdayScraper(url)
        return scraper.parse()

    else:
        return None
    return