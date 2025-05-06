

class BaseScraper:
    """
    An abstract base class for web scrapers.
    """
    def __init__(self, url, headers=None):
        """
        Initializes the scraper with a URL and optional headers.
        """
        self.url = url
        self.headers = headers

    def fetch_html(self):
        """
        Fetches the HTML content of the URL.
        Subclasses should implement their own fetching logic (e.g., with requests or Selenium).
        """
        raise NotImplementedError("Subclasses must implement the fetch_html method.")

    def parse(self):
        """
        Orchestrates the scraping and parsing process.
        Subclasses should implement their specific parsing logic.
        """
        raise NotImplementedError("Subclasses must implement the parse method.")

    def parse_requirements(self, html):
        """
        Parses the job requirements from the HTML.
        Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement the parse_requirements method.")

    def parse_description(self, html):
        """
        Parses the job description from the HTML.
        Subclasses must implement this method.
        """
        raise NotImplementedError("Subclasses must implement the parse_description method.")

    def save_data(self, data, filename):
        """
        Saves the extracted data to a file.
        This might be implemented here or in a utility class.
        """
        pass # Or could be implemented here for common saving logic