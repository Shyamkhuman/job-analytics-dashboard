"""
Data Visualization Module
Create charts for salary trends, skills demand, and market patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from collections import Counter
import os

# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class JobMarketVisualizer:
    """Create visualizations for job market analysis"""

    def __init__(self, df: pd.DataFrame, output_dir: str = 'outputs/charts'):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def create_skills_bar_chart(self, top_n: int = 15, save: bool = True,
                                 show: bool = False) -> plt.Figure:
        """Create bar chart of top in-demand skills"""
        all_skills = [skill for skills in self.df['skills_extracted'].dropna()
                      for skill in skills]
        skill_counts = Counter(all_skills).most_common(top_n)

        skills = [s[0] for s in skill_counts]
        counts = [s[1] for s in skill_counts]

        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(skills, counts, color=plt.cm.viridis(np.linspace(0.3, 0.9, len(skills))))

        ax.set_xlabel('Number of Job Postings', fontsize=12)
        ax.set_ylabel('Skills', fontsize=12)
        ax.set_title('Top In-Demand Skills in Job Market', fontsize=14, fontweight='bold')
        ax.invert_yaxis()

        # Add value labels
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(count), va='center', fontsize=10)

        plt.tight_layout()

        if save:
            plt.savefig(f'{self.output_dir}/top_skills.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {self.output_dir}/top_skills.png")

        if show:
            plt.show()

        return fig

    def create_skills_by_category(self, categories: Dict[str, List[str]] = None,
                                   save: bool = True, show: bool = False) -> plt.Figure:
        """Create grouped bar chart of skills by category"""
        if categories is None:
            categories = {
                'Programming': ['Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust'],
                'Web': ['React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'HTML', 'CSS'],
                'Data/AI': ['SQL', 'Machine Learning', 'Deep Learning', 'Pandas', 'NumPy', 'Tableau'],
                'DevOps': ['Docker', 'Kubernetes', 'Terraform', 'CI/CD', 'AWS', 'Azure', 'GCP']
            }

        all_skills = [skill for skills in self.df['skills_extracted'].dropna()
                      for skill in skills]
        skill_counts = Counter(all_skills)

        fig, ax = plt.subplots(figsize=(14, 8))

        y_pos = 0
        y_labels = []
        y_values = []

        for category, skills_list in categories.items():
            for skill in skills_list:
                if skill in skill_counts and skill_counts[skill] > 0:
                    y_labels.append(f"{category}: {skill}")
                    y_values.append(skill_counts[skill])

        if not y_values:
            print("No skills found for specified categories")
            return None

        colors = plt.cm.Set3(np.linspace(0, 1, len(y_labels)))
        bars = ax.barh(y_labels, y_values, color=colors)

        ax.set_xlabel('Number of Job Postings', fontsize=12)
        ax.set_title('Skills Demand by Category', fontsize=14, fontweight='bold')
        ax.invert_yaxis()

        # Add value labels
        for bar, count in zip(bars, y_values):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                   str(int(count)), va='center', fontsize=9)

        plt.tight_layout()

        if save:
            plt.savefig(f'{self.output_dir}/skills_by_category.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {self.output_dir}/skills_by_category.png")

        if show:
            plt.show()

        return fig

    def create_location_heatmap(self, save: bool = True, show: bool = False) -> plt.Figure:
        """Create heatmap of job demand by location"""
        location_counts = self.df['location'].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(10, 6))

        # Create horizontal bar chart (better for locations)
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(location_counts)))
        bars = ax.barh(location_counts.index, location_counts.values, color=colors)

        ax.set_xlabel('Number of Jobs', fontsize=12)
        ax.set_title('Job Demand by Location (Top 10)', fontsize=14, fontweight='bold')

        # Add value labels
        for bar, count in zip(bars, location_counts.values):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(int(count)), va='center', fontsize=10)

        plt.tight_layout()

        if save:
            plt.savefig(f'{self.output_dir}/location_demand.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {self.output_dir}/location_demand.png")

        if show:
            plt.show()

        return fig

    def create_salary_distribution(self, save: bool = True, show: bool = False) -> plt.Figure:
        """Create histogram of salary distribution"""
        import re

        salaries = []
        for salary in self.df['salary'].dropna():
            numbers = re.findall(r'\d+', str(salary))
            if numbers:
                avg = np.mean([float(n) for n in numbers[:2]])
                salaries.append(avg)

        if not salaries:
            print("No salary data available")
            return None

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Histogram
        axes[0].hist(salaries, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        axes[0].axvline(np.mean(salaries), color='red', linestyle='--',
                       label=f'Mean: {np.mean(salaries):,.0f}')
        axes[0].axvline(np.median(salaries), color='green', linestyle='--',
                       label=f'Median: {np.median(salaries):,.0f}')
        axes[0].set_xlabel('Salary')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Salary Distribution', fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Box plot
        axes[1].boxplot(salaries, vert=False, patch_artist=True,
                       boxprops=dict(facecolor='lightblue'))
        axes[1].set_xlabel('Salary')
        axes[1].set_title('Salary Box Plot', fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            plt.savefig(f'{self.output_dir}/salary_distribution.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {self.output_dir}/salary_distribution.png")

        if show:
            plt.show()

        return fig

    def create_experience_level_chart(self, save: bool = True, show: bool = False) -> plt.Figure:
        """Create pie chart of jobs by experience level"""
        experience_keywords = {
            'Entry Level': ['fresher', 'entry level', 'junior', 'trainee', '0-2 years'],
            'Mid Level': ['mid level', 'mid-level', '2-5 years', '3-5 years'],
            'Senior Level': ['senior', 'lead', 'principal', '5+ years', '8+ years', 'manager'],
        }

        counts = {}
        for level, keywords in experience_keywords.items():
            mask = self.df['title'].str.lower().str.contains('|'.join(keywords), na=False)
            counts[level] = mask.sum()

        # Add unclassified
        classified = sum(counts.values())
        counts['Other'] = len(self.df) - classified

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(counts)))

        wedges, texts, autotexts = ax.pie(counts.values(), labels=counts.keys(),
                                           autopct='%1.1f%%', colors=colors,
                                           explode=[0.02]*len(counts))

        ax.set_title('Jobs by Experience Level', fontsize=14, fontweight='bold')

        plt.tight_layout()

        if save:
            plt.savefig(f'{self.output_dir}/experience_levels.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {self.output_dir}/experience_levels.png")

        if show:
            plt.show()

        return fig

    def create_skill_correlation_matrix(self, top_n: int = 12,
                                         save: bool = True, show: bool = False) -> plt.Figure:
        """Create correlation heatmap of skills"""
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

        df_corr = pd.DataFrame(cooccurrence)

        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(df_corr, annot=True, fmt='d', cmap='YlOrRd',
                   square=True, linewidths=0.5, ax=ax)

        ax.set_title('Skill Co-occurrence Matrix (Top Skills)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Skills', fontsize=12)
        ax.set_ylabel('Skills', fontsize=12)

        plt.tight_layout()

        if save:
            plt.savefig(f'{self.output_dir}/skill_correlation.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {self.output_dir}/skill_correlation.png")

        if show:
            plt.show()

        return fig

    def create_source_comparison(self, save: bool = True, show: bool = False) -> plt.Figure:
        """Compare job counts across different sources"""
        if 'source' not in self.df.columns:
            print("No 'source' column in data")
            return None

        source_counts = self.df['source'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.Accent(np.linspace(0, 1, len(source_counts)))

        bars = ax.bar(source_counts.index, source_counts.values, color=colors)

        ax.set_xlabel('Job Portal', fontsize=12)
        ax.set_ylabel('Number of Jobs', fontsize=12)
        ax.set_title('Jobs by Source Portal', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)

        # Add value labels
        for bar, count in zip(bars, source_counts.values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   str(int(count)), ha='center', fontsize=10)

        plt.tight_layout()

        if save:
            plt.savefig(f'{self.output_dir}/source_comparison.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {self.output_dir}/source_comparison.png")

        if show:
            plt.show()

        return fig

    def create_all_charts(self):
        """Generate all available charts"""
        print("Generating all visualizations...")

        self.create_skills_bar_chart()
        self.create_skills_by_category()
        self.create_location_heatmap()
        self.create_salary_distribution()
        self.create_experience_level_chart()
        self.create_skill_correlation_matrix()
        self.create_source_comparison()

        print(f"\nAll charts saved to {self.output_dir}/")


if __name__ == "__main__":
    # Example usage
    try:
        df = pd.read_csv('data/jobs_data_latest.csv')

        # Ensure skills_extracted is parsed as list
        if 'skills_extracted' in df.columns:
            df['skills_extracted'] = df['skills_extracted'].apply(
                lambda x: eval(x) if isinstance(x, str) else x)

        visualizer = JobMarketVisualizer(df)

        print("\n" + "="*50)
        print("GENERATING VISUALIZATIONS")
        print("="*50 + "\n")

        visualizer.create_all_charts()

        print("\nDone! Check the outputs/charts folder for all visualizations.")

    except FileNotFoundError:
        print("No job data found. Run the scraper first!")
