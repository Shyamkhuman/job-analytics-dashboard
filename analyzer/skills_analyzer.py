"""
Skills Analyzer Module
Analyzes job data to identify trending skills, roles, and market demand
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
from datetime import datetime
import re


class SkillsAnalyzer:
    """Analyze job market data to extract insights about skills and trends"""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize with job data DataFrame

        Args:
            df: DataFrame with columns: title, company, location, salary,
                description, skills_extracted, scraped_date, source
        """
        self.df = df
        self.skill_trends = {}

    def get_top_skills(self, n: int = 20) -> pd.DataFrame:
        """Get the most in-demand skills"""
        all_skills = [skill for skills in self.df['skills_extracted'].dropna()
                      for skill in skills]
        skill_counts = Counter(all_skills)

        result = pd.DataFrame({
            'skill': list(skill_counts.keys()),
            'demand_count': list(skill_counts.values())
        })
        result = result.sort_values('demand_count', ascending=False).head(n)
        result['percentage'] = (result['demand_count'] / len(self.df) * 100).round(2)

        return result.reset_index(drop=True)

    def get_top_skills_by_category(self, categories: Dict[str, List[str]] = None) -> Dict:
        """
        Get top skills grouped by category

        Args:
            categories: Optional dict mapping category names to skill lists
        """
        if categories is None:
            categories = {
                'Programming Languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust'],
                'Frontend': ['React', 'Angular', 'Vue', 'HTML', 'CSS', 'SASS'],
                'Backend': ['Node.js', 'Django', 'Flask', 'FastAPI', 'Spring Boot'],
                'Databases': ['SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis'],
                'Cloud': ['AWS', 'Azure', 'GCP'],
                'DevOps': ['Docker', 'Kubernetes', 'Terraform', 'CI/CD'],
                'ML/AI': ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn'],
                'Data Analysis': ['Pandas', 'NumPy', 'Matplotlib', 'Tableau', 'Power BI'],
            }

        all_skills = [skill for skills in self.df['skills_extracted'].dropna()
                      for skill in skills]
        skill_counts = Counter(all_skills)

        results = {}
        for category, skills_list in categories.items():
            category_skills = [(s, skill_counts.get(s, 0)) for s in skills_list
                               if skill_counts.get(s, 0) > 0]
            category_skills.sort(key=lambda x: x[1], reverse=True)
            results[category] = category_skills

        return results

    def analyze_by_experience_level(self) -> Dict:
        """Categorize jobs by experience level and analyze skill requirements"""
        experience_keywords = {
            'Entry Level': ['fresher', 'entry level', 'junior', 'trainee', '0-2 years', '0-1 years'],
            'Mid Level': ['mid level', 'mid-level', '2-5 years', '3-5 years', 'senior'],
            'Senior Level': ['senior', 'lead', 'principal', '5+ years', '8+ years', 'manager'],
        }

        results = {}
        for level, keywords in experience_keywords.items():
            mask = self.df['title'].str.lower().str.contains('|'.join(keywords), na=False)
            level_df = self.df[mask]

            if len(level_df) > 0:
                all_skills = [skill for skills in level_df['skills_extracted'].dropna()
                              for skill in skills]
                top_skills = Counter(all_skills).most_common(10)

                results[level] = {
                    'job_count': len(level_df),
                    'top_skills': top_skills,
                    'avg_salary': self._extract_avg_salary(level_df)
                }

        return results

    def _extract_avg_salary(self, df: pd.DataFrame) -> float:
        """Extract and calculate average salary from salary strings"""
        salaries = []
        for salary in df['salary'].dropna():
            # Extract numeric values from salary strings
            numbers = re.findall(r'\d+', str(salary))
            if numbers:
                # Handle different salary formats
                avg = np.mean([float(n) for n in numbers[:2]])
                # Normalize to annual if monthly indicated
                if 'month' in str(salary).lower() or 'lakhs' in str(salary).lower():
                    avg *= 12
                salaries.append(avg)

        return np.mean(salaries) if salaries else 0

    def get_location_demand(self) -> pd.DataFrame:
        """Analyze job demand by location"""
        location_counts = self.df['location'].value_counts().head(15)

        result = pd.DataFrame({
            'location': location_counts.index,
            'job_count': location_counts.values
        })
        result['percentage'] = (result['job_count'] / len(self.df) * 100).round(2)

        return result.reset_index(drop=True)

    def get_company_hiring_trends(self, top_n: int = 20) -> pd.DataFrame:
        """Analyze which companies are hiring the most"""
        company_counts = self.df['company'].value_counts().head(top_n)

        result = pd.DataFrame({
            'company': company_counts.index,
            'openings': company_counts.values
        })

        return result.reset_index(drop=True)

    def analyze_salary_trends(self, skill: str = None) -> Dict:
        """
        Analyze salary trends overall or for a specific skill

        Args:
            skill: Optional skill name to filter by
        """
        df = self.df.copy()

        if skill:
            mask = df['skills_extracted'].apply(lambda x: skill in x if isinstance(x, list) else False)
            df = df[mask]

        salaries = []
        for salary in df['salary'].dropna():
            numbers = re.findall(r'\d+', str(salary))
            if numbers:
                avg = np.mean([float(n) for n in numbers[:2]])
                salaries.append(avg)

        if not salaries:
            return {'message': 'No salary data available'}

        return {
            'average': np.mean(salaries),
            'median': np.median(salaries),
            'min': np.min(salaries),
            'max': np.max(salaries),
            'std_dev': np.std(salaries),
            'sample_size': len(salaries)
        }

    def get_skill_correlations(self, top_n: int = 15) -> pd.DataFrame:
        """Find skills that frequently appear together"""
        all_skills = [skill for skills in self.df['skills_extracted'].dropna()
                      for skill in skills]
        top_skills = [s for s, _ in Counter(all_skills).most_common(top_n)]

        # Create co-occurrence matrix
        cooccurrence = {s1: {s2: 0 for s2 in top_skills} for s1 in top_skills}

        for skills_list in self.df['skills_extracted'].dropna():
            for s1 in skills_list:
                if s1 in top_skills:
                    for s2 in skills_list:
                        if s2 in top_skills and s1 != s2:
                            cooccurrence[s1][s2] += 1

        # Convert to DataFrame
        df = pd.DataFrame(cooccurrence)
        return df

    def generate_insights(self) -> Dict:
        """Generate comprehensive market insights"""
        top_skills = self.get_top_skills(15)
        location_demand = self.get_location_demand()
        experience_analysis = self.analyze_by_experience_level()
        salary_analysis = self.analyze_salary_trends()

        insights = {
            'summary': {
                'total_jobs_analyzed': len(self.df),
                'unique_companies': self.df['company'].nunique(),
                'unique_locations': self.df['location'].nunique(),
                'data_sources': self.df['source'].unique().tolist(),
            },
            'top_skills': top_skills.to_dict('records'),
            'location_demand': location_demand.to_dict('records'),
            'experience_breakdown': experience_analysis,
            'salary_insights': salary_analysis,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        return insights

    def export_analysis(self, output_path: str = 'data/analysis_results.json'):
        """Export analysis results to JSON"""
        import json
        insights = self.generate_insights()

        with open(output_path, 'w') as f:
            json.dump(insights, f, indent=2, default=str)

        print(f"Analysis exported to {output_path}")
        return insights


if __name__ == "__main__":
    # Example usage
    try:
        df = pd.read_csv('data/jobs_data_latest.csv')
        analyzer = SkillsAnalyzer(df)

        print("\n" + "="*50)
        print("SKILLS ANALYSIS REPORT")
        print("="*50)

        insights = analyzer.generate_insights()

        print(f"\nTotal Jobs Analyzed: {insights['summary']['total_jobs_analyzed']}")

        print("\n📊 TOP 10 IN-DEMAND SKILLS:")
        for i, skill in enumerate(insights['top_skills'][:10], 1):
            print(f"  {i}. {skill['skill']}: {skill['demand_count']} jobs ({skill['percentage']}%)")

        print("\n📍 TOP LOCATIONS:")
        for i, loc in enumerate(insights['location_demand'][:5], 1):
            print(f"  {i}. {loc['location']}: {loc['job_count']} jobs")

        print("\n💰 SALARY INSIGHTS:")
        if 'average' in insights['salary_insights']:
            print(f"  Average: {insights['salary_insights']['average']:,.0f}")
            print(f"  Median: {insights['salary_insights']['median']:,.0f}")

    except FileNotFoundError:
        print("No job data found. Run the scraper first!")
