"""
Job Scraper Module
Scrapes job postings from various online job portals
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import pandas as pd
import re
import time
from datetime import datetime


class JobScraper:
    """Base class for scraping job postings from various portals"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.jobs_data = []

    def scrape_linkedin(self, keywords: str, location: str = "", limit: int = 50) -> List[Dict]:
        """
        Scrape job listings from LinkedIn
        Note: LinkedIn requires authentication for full access
        This is a template that can be adapted with API access
        """
        jobs = []
        print(f"Searching LinkedIn for: {keywords}")
        # Implementation would require LinkedIn API or authenticated session
        return jobs

    def scrape_indeed(self, keywords: str, location: str = "", limit: int = 50) -> List[Dict]:
        """
        Scrape job listings from Indeed
        """
        jobs = []
        start = 0

        while len(jobs) < limit:
            url = f"https://www.indeed.com/jobs?q={keywords.replace(' ', '+')}&l={location.replace(' ', '+')}&start={start}"

            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'lxml')

                job_cards = soup.find_all('div', class_='job_seen_beacon')

                if not job_cards:
                    break

                for card in job_cards[:limit - len(jobs)]:
                    job = self._parse_indeed_job(card, keywords)
                    if job:
                        jobs.append(job)

                start += 10
                time.sleep(1)  # Be respectful to the server

            except Exception as e:
                print(f"Error scraping Indeed: {e}")
                break

        return jobs

    def _parse_indeed_job(self, card, keywords: str) -> Dict:
        """Parse individual Indeed job card"""
        try:
            title_elem = card.find('h2', class_='jobTitle')
            company_elem = card.find('span', class_='companyName')
            location_elem = card.find('div', class_='companyLocation')
            salary_elem = card.find('span', class_='salaryText')
            desc_elem = card.find('div', class_='job-snippet')

            return {
                'title': title_elem.text.strip() if title_elem else '',
                'company': company_elem.text.strip() if company_elem else '',
                'location': location_elem.text.strip() if location_elem else '',
                'salary': salary_elem.text.strip() if salary_elem else '',
                'description': desc_elem.text.strip() if desc_elem else '',
                'skills_extracted': self._extract_skills(desc_elem.text if desc_elem else '', keywords),
                'scraped_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Indeed'
            }
        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None

    def scrape_glassdoor(self, keywords: str, location: str = "", limit: int = 50) -> List[Dict]:
        """
        Scrape job listings from Glassdoor
        """
        jobs = []
        print(f"Searching Glassdoor for: {keywords}")
        # Glassdoor has anti-scraping measures - would need API or Selenium
        return jobs

    def scrape_naukri(self, keywords: str, location: str = "", limit: int = 50) -> List[Dict]:
        """
        Scrape job listings from Naukri.com (popular in India)
        """
        jobs = []

        for page in range(1, (limit // 20) + 2):
            url = f"https://www.naukri.com/{keywords.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}?pageid={page}"

            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'lxml')

                job_cards = soup.find_all('article', class_='jobTuple')

                if not job_cards:
                    break

                for card in job_cards:
                    job = self._parse_naukri_job(card, keywords)
                    if job:
                        jobs.append(job)

                time.sleep(1)

            except Exception as e:
                print(f"Error scraping Naukri: {e}")
                break

        return jobs

    def _parse_naukri_job(self, card, keywords: str) -> Dict:
        """Parse individual Naukri job card"""
        try:
            title_elem = card.find('a', class_='title')
            company_elem = card.find('a', class_='subTitle')
            location_elem = card.find('span', class_='location')
            salary_elem = card.find('span', class_='salary')
            desc_elem = card.find('div', class_='job-description')
            skills_elem = card.find_all('span', class_='roundTuple')

            skills = [s.text.strip() for s in skills_elem]

            return {
                'title': title_elem.text.strip() if title_elem else '',
                'company': company_elem.text.strip() if company_elem else '',
                'location': location_elem.text.strip() if location_elem else '',
                'salary': salary_elem.text.strip() if salary_elem else '',
                'description': desc_elem.text.strip() if desc_elem else '',
                'skills_extracted': skills if skills else self._extract_skills(desc_elem.text if desc_elem else '', keywords),
                'scraped_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'Naukri'
            }
        except Exception as e:
            print(f"Error parsing Naukri job card: {e}")
            return None

    def _extract_skills(self, description: str, keywords: str) -> List[str]:
        """Extract relevant skills from job description"""
        # Common tech skills to look for
        common_skills = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'FastAPI',
            'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn',
            'Pandas', 'NumPy', 'Matplotlib', 'Tableau', 'Power BI',
            'Git', 'CI/CD', 'Agile', 'Scrum', 'REST API', 'GraphQL',
            'HTML', 'CSS', 'SASS', 'Webpack', 'Vite'
        ]

        found_skills = []
        description_lower = description.lower()

        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)

        return found_skills

    def scrape_all_sources(self, keywords: str, location: str = "", limit: int = 100) -> pd.DataFrame:
        """
        Scrape from all available sources and return combined DataFrame
        """
        all_jobs = []

        sources = [
            ('Indeed', self.scrape_indeed),
            ('Naukri', self.scrape_naukri),
        ]

        for source_name, scraper_func in sources:
            print(f"\n{'='*50}")
            print(f"Scraping {source_name}...")
            print(f"{'='*50}")

            try:
                jobs = scraper_func(keywords, location, limit // len(sources))
                all_jobs.extend(jobs)
                print(f"Found {len(jobs)} jobs from {source_name}")
            except Exception as e:
                print(f"Failed to scrape {source_name}: {e}")

        df = pd.DataFrame(all_jobs)
        return df

    def save_to_csv(self, df: pd.DataFrame, filename: str = None):
        """Save scraped data to CSV"""
        if filename is None:
            filename = f"jobs_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        df.to_csv(f"data/{filename}", index=False)
        print(f"Data saved to data/{filename}")


if __name__ == "__main__":
    # Example usage
    scraper = JobScraper()

    keywords = input("Enter job keywords to search: ")
    location = input("Enter location (or leave blank): ")

    print(f"\nStarting job search for '{keywords}' in '{location or 'Anywhere'}'...")

    df = scraper.scrape_all_sources(keywords, location)

    if not df.empty:
        scraper.save_to_csv(df)
        print(f"\nTotal jobs found: {len(df)}")
        print(f"\nTop skills required:")
        all_skills = [skill for skills in df['skills_extracted'] for skill in skills]
        from collections import Counter
        skill_counts = Counter(all_skills)
        for skill, count in skill_counts.most_common(15):
            print(f"  {skill}: {count}")
    else:
        print("No jobs found. Try different keywords or check your internet connection.")
