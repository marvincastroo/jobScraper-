from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper  # Import the base class
import time


class LinkedInScraper(BaseScraper):

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

    def _parse_content(self, soup):
        """Parses the relevant information from the BeautifulSoup object."""
        data = {}

        # data = {"url": self.url}
        # Example: Extract job title (you'll need to inspect the actual HTML)
        title_element = soup.select_one('h1')
        # data["title"] = title_element.text.strip() if title_element else None

        # Example: Extract job description (you'll need to inspect the actual HTML)
        description_element = soup.find('div', {'class': 'show-more-less-html__markup'})
        data["description"] = description_element.get_text(separator='\n').strip() if description_element else None

        return data


if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/view/4221009877/"
    scraper = LinkedInScraper(url=url)
    data = scraper.parse()
    if data:
        print("Extracted data:")
        # print(f"Title: {data.get("Title")}")
        print(f"Description: {data.get("description")}")
        # save_data(data, f"data/{platform}_job_{job_urls.index(url)}.json")
    else:
        print(f"Failed to extract data from: {url}")