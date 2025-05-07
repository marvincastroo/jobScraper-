from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
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

    def _parse_content(self, soup):
        """Parses the relevant information from the BeautifulSoup object."""
        data = {}

        about_role = soup.find('p', style='text-align:left', string="About the Role")
        # about_role_text = ""
        if about_role:
            next_s = about_role.next_sibling
            if next_s:
                next_child = next_s.next_element
                next_child_text = next_child.getText()
                data["about_role"] = next_child_text

        responsibilities_heading = soup.find('b',  string="Responsibilities")
        if responsibilities_heading:
            ul_element = responsibilities_heading.find_parent().next_sibling
            if ul_element:
                data["responsibilities"] = ul_element.getText()

        requirements = soup.find('b', string = "About You")
        if requirements:
            basic_requirements = requirements.find_parent().next_sibling.next_sibling
            if basic_requirements:
                basic_req = basic_requirements.next_sibling
                if basic_req:
                    data["requirements"] = basic_req.getText()
            # other_requirements









        return data


if __name__ == "__main__":
    url = "https://workday.wd5.myworkdayjobs.com/Workday/job/Costa-Rica/Salesforce-Business-Systems-Analyst--Global-Customer-Support-_JR-0096614"
    scraper = WorkdayScraper(url=url)
    data = scraper.parse()
    if data:
        print("Extracted data:")
        # print(f"Title: {data.get("Title")}")
        print(data)
        print(f"Description: {data.get("responsibilities")}")
        # save_data(data, f"data/{platform}_job_{job_urls.index(url)}.json")
    else:
        print(f"Failed to extract data from: {url}")