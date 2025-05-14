from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from src.core.prompt_manager import get_prompt_template_from_jinja2
from bs4 import BeautifulSoup
from src.core.llm import get_model_response
from src.scrapers.base_scraper import BaseScraper  # Import the base class
import time


class WorkdayScraper(BaseScraper):

    def __init__(self, url, headers=None):
        super().__init__(url, headers)
        self.driver = None  # Initialize driver

    def _setup_driver(self):
        """Sets up the Selenium WebDriver."""
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")

        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def _close_driver(self):
        """Closes the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()

    def parse(self):
        """Orchestrates the scraping and parsing process for LinkedIn."""
        self._setup_driver()
        try:
            self.driver.get(self.url)
            time.sleep(5)  # Adjust as needed
            # LinkedIn often loads more content dynamically, you might need to scroll
            # or wait for specific elements here.
            rendered_html = self.driver.page_source
            soup = BeautifulSoup(rendered_html, 'html.parser')
            with open("file.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())

            return self._parse_content(soup)
        except Exception as e:
            print(f"Error scraping LinkedIn URL '{self.url}': {e}")
            return None
        finally:
            self._close_driver()


    def _llm_synthesis(self, content):
        sys_prompt = get_prompt_template_from_jinja2(prompt_path='../prompts',
                                                     prompt_name='scrapper.txt')
        response = get_model_response(system_prompt=sys_prompt,
                                      user_prompt=content)


        return response
    def _parse_content(self, soup):
        """Parses the relevant information from the BeautifulSoup object."""

        description_meta_name = soup.find('meta', {'name': 'description'})
        description_content_name = description_meta_name['content'] if description_meta_name else None


        # feed content into LLM to get key values - too lazy and clueless with scraping to do this myself
        llm_response = self._llm_synthesis(description_content_name)
        job_summary = llm_response.choices[0].message.content

        return job_summary


if __name__ == "__main__":
    url = "https://workday.wd5.myworkdayjobs.com/Workday/job/Costa-Rica/Salesforce-Business-Systems-Analyst--Global-Customer-Support-_JR-0096614"
    scraper = WorkdayScraper(url=url)
    data = scraper.parse()
    if data:
        print("Extracted data:")
        # print(f"Title: {data.get("Title")}")
        print(data)
        # print(f"Description: {data.get("responsibilities")}")
        # save_data(data, f"data/{platform}_job_{job_urls.index(url)}.json")
    else:
        print(f"Failed to extract data from: {url}")