from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from base_scraper import BaseScraper  # Import the base class
import time


class LinkedInScraper(BaseScraper):

    def __init__(self, url, headers=None):
        super().__init__(url, headers)
        self.driver = None  # Initialize driver

    def _setup_driver(self):
        """Sets up the Selenium WebDriver."""
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    def _close_driver(self):
        """Closes the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()

    def parse(self):
        """Orchestrates the scraping and parsing process for LinkedIn."""
        self._setup_driver()
        try:
            self.driver.get(self.url)
            time.sleep(3)  # Adjust as needed
            # LinkedIn often loads more content dynamically, you might need to scroll
            # or wait for specific elements here.
            rendered_html = self.driver.page_source
            soup = BeautifulSoup(rendered_html, 'html.parser')
            return self._parse_content(soup)
        except Exception as e:
            print(f"Error scraping LinkedIn URL '{self.url}': {e}")
            return None
        finally:
            self._close_driver()

    def _parse_content(self, soup):
        """Parses the relevant information from the BeautifulSoup object."""


        data = {"url": self.url}
        # Example: Extract job title (you'll need to inspect the actual HTML)
        title_element = soup.find('h1', {'class': 'top-card-layout__title'})
        data["title"] = title_element.text.strip() if title_element else None

        # Example: Extract job description (you'll need to inspect the actual HTML)
        description_element = soup.find('div', {'class': 'show-more-less-html__markup'})
        data["description"] = description_element.get_text(separator='\n').strip() if description_element else None

        # Example: Extract requirements (you'll need to inspect the actual HTML)
        # LinkedIn's structure can be complex, you'll need to carefully inspect
        requirements_section = soup.find('h2', string=lambda text: text and 'Qualifications' in text) or \
                               soup.find('h2', string=lambda text: text and 'Requirements' in text)

        if requirements_section:
            requirements_list = []
            ul_elements = requirements_section.find_all_next('ul', limit=2)  # Adjust limit as needed
            for ul in ul_elements:
                for li in ul.find_all('li'):
                    requirements_list.append(li.text.strip())
            data["requirements"] = requirements_list
        else:
            data["requirements"] = None

        return data


if __name__ == "__main__":
    url = "https://www.linkedin.com/jobs/view/4222612542/"
    scraper = LinkedInScraper(url="https://www.linkedin.com/jobs/view/4222612542/")
    data = scraper.parse()
    if data:
        print("Extracted data:", data)
        # save_data(data, f"data/{platform}_job_{job_urls.index(url)}.json")
    else:
        print(f"Failed to extract data from: {url}")