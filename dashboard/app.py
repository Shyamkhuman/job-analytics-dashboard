"""
Streamlit Dashboard for Job Analytics Platform
Interactive web interface for exploring job market insights
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import os
import re
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Job Market Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stDataFrame {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def load_data(data_dir: str = '../data') -> pd.DataFrame:
    """Load the latest job data from CSV files"""
    try:
        files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not files:
            return None

        latest_file = max(files)
        df = pd.read_csv(os.path.join(data_dir, latest_file))

        # Parse skills_extracted if stored as string
        if 'skills_extracted' in df.columns:
            df['skills_extracted'] = df['skills_extracted'].apply(
                lambda x: eval(x) if isinstance(x, str) and x != 'nan' else []
            )

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def extract_salaries(df: pd.DataFrame) -> list:
    """Extract numeric salaries from salary strings"""
    salaries = []
    for salary in df['salary'].dropna():
        numbers = re.findall(r'\d+', str(salary))
        if numbers:
            avg = np.mean([float(n) for n in numbers[:2]])
            salaries.append(avg)
    return salaries


def main():
    # Header
    st.markdown('<p class="main-header">📊 Job Market Analytics Platform</p>',
                unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Go to:",
        ["Dashboard", "Skills Analysis", "Location Insights", "Salary Trends", "Upload Data"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    ### About
    This platform analyzes job postings to identify:
    - 🔍 Trending skills
    - 📈 Market demand
    - 💰 Salary trends
    - 🌍 Location insights
    """)

    # Load data
    df = load_data()

    if page == "Upload Data":
        show_upload_page()
        return

    if df is None or df.empty:
        st.warning("""
        ### No Data Available
        Please upload job data or run the scraper first.

        **Steps:**
        1. Go to 'Upload Data' page to upload a CSV file, OR
        2. Run the scraper: `python scraper/job_scraper.py`
        """)
        return

    # Dashboard Page
    if page == "Dashboard":
        show_dashboard(df)

    # Skills Analysis Page
    elif page == "Skills Analysis":
        show_skills_analysis(df)

    # Location Insights Page
    elif page == "Location Insights":
        show_location_insights(df)

    # Salary Trends Page
    elif page == "Salary Trends":
        show_salary_trends(df)


def show_dashboard(df):
    """Main dashboard overview"""
    st.header("Market Overview")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Jobs", f"{len(df):,}")

    with col2:
        st.metric("Unique Companies", f"{df['company'].nunique():,}")

    with col3:
        st.metric("Locations", f"{df['location'].nunique():,}")

    with col4:
        st.metric("Data Sources", f"{df['source'].nunique() if 'source' in df.columns else 1}")

    st.markdown("---")

    # Top skills chart
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🔥 Top 15 In-Demand Skills")

        all_skills = [skill for skills in df['skills_extracted'].dropna() for skill in skills]
        skill_counts = Counter(all_skills).most_common(15)

        skills_df = pd.DataFrame(skill_counts, columns=['Skill', 'Count'])

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(skills_df)))
        bars = ax.barh(skills_df['Skill'], skills_df['Count'], color=colors)
        ax.set_xlabel('Job Postings')
        ax.set_title('Top Skills Demand')
        ax.invert_yaxis()

        for bar, count in zip(bars, skills_df['Count']):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(int(count)), va='center', fontsize=9)

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("📊 Experience Distribution")

        experience_keywords = {
            'Entry': ['fresher', 'entry level', 'junior', 'trainee', '0-2 years'],
            'Mid': ['mid level', 'mid-level', '2-5 years', '3-5 years'],
            'Senior': ['senior', 'lead', 'principal', '5+ years', 'manager'],
        }

        exp_counts = {}
        for level, keywords in experience_keywords.items():
            mask = df['title'].str.lower().str.contains('|'.join(keywords), na=False)
            exp_counts[level] = mask.sum()
        exp_counts['Other'] = len(df) - sum(exp_counts.values())

        fig, ax = plt.subplots(figsize=(6, 6))
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(exp_counts)))
        ax.pie(exp_counts.values(), labels=exp_counts.keys(), autopct='%1.1f%%',
              colors=colors, explode=[0.02]*len(exp_counts))
        ax.set_title('By Experience Level')

        plt.tight_layout()
        st.pyplot(fig)

    # Recent jobs table
    st.markdown("---")
    st.subheader("📋 Recent Job Postings")

    display_df = df[['title', 'company', 'location', 'source', 'scraped_date']].head(10)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def show_skills_analysis(df):
    """Detailed skills analysis page"""
    st.header("Skills Analysis")

    # Category selection
    categories = {
        'Programming Languages': ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go'],
        'Frontend': ['React', 'Angular', 'Vue', 'HTML', 'CSS'],
        'Backend': ['Node.js', 'Django', 'Flask', 'FastAPI', 'Spring Boot'],
        'Databases': ['SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis'],
        'Cloud': ['AWS', 'Azure', 'GCP'],
        'DevOps': ['Docker', 'Kubernetes', 'Terraform', 'CI/CD'],
        'ML/AI': ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn'],
        'Data': ['Pandas', 'NumPy', 'Matplotlib', 'Tableau', 'Power BI'],
    }

    all_skills = [skill for skills in df['skills_extracted'].dropna() for skill in skills]
    skill_counts = Counter(all_skills)

    # Category breakdown
    st.subheader("Skills by Category")

    selected_category = st.selectbox("Select Category", list(categories.keys()))

    cat_skills = [(s, skill_counts.get(s, 0)) for s in categories[selected_category]
                  if skill_counts.get(s, 0) > 0]
    cat_skills.sort(key=lambda x: x[1], reverse=True)

    if cat_skills:
        cat_df = pd.DataFrame(cat_skills, columns=['Skill', 'Demand'])

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(cat_df)))
        ax.bar(cat_df['Skill'], cat_df['Demand'], color=colors)
        ax.set_xlabel('Skill')
        ax.set_ylabel('Job Postings')
        ax.set_title(f'{selected_category} - Demand Analysis')
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        st.pyplot(fig)

        st.dataframe(cat_df, use_container_width=True, hide_index=True)
    else:
        st.info("No data found for this category")

    # Skill correlation
    st.markdown("---")
    st.subheader("🔗 Skill Correlations")

    top_n = st.slider("Number of top skills to analyze", 5, 20, 10)
    top_skills = [s for s, _ in skill_counts.most_common(top_n)]

    # Co-occurrence matrix
    cooccurrence = {s1: {s2: 0 for s2 in top_skills} for s1 in top_skills}
    for skills_list in df['skills_extracted'].dropna():
        for s1 in skills_list:
            if s1 in top_skills:
                for s2 in skills_list:
                    if s2 in top_skills and s1 != s2:
                        cooccurrence[s1][s2] += 1

    corr_df = pd.DataFrame(cooccurrence)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_df, annot=True, fmt='d', cmap='YlOrRd', square=True,
               linewidths=0.5, ax=ax)
    ax.set_title('Skill Co-occurrence')
    plt.tight_layout()

    st.pyplot(fig)


def show_location_insights(df):
    """Location-based insights page"""
    st.header("Location Insights")

    location_counts = df['location'].value_counts().head(15)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Locations by Job Count")

        fig, ax = plt.subplots(figsize=(8, 8))
        colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(location_counts)))
        bars = ax.barh(location_counts.index, location_counts.values, color=colors)
        ax.set_xlabel('Job Postings')
        ax.set_title('Geographic Demand')
        ax.invert_yaxis()

        for bar, count in zip(bars, location_counts.values):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(int(count)), va='center', fontsize=9)

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Location Statistics")

        loc_stats = pd.DataFrame({
            'Location': location_counts.index,
            'Jobs': location_counts.values,
            'Percentage': (location_counts.values / len(df) * 100).round(2)
        })

        st.dataframe(loc_stats, use_container_width=True, hide_index=True)

    # Company hiring by location
    st.markdown("---")
    st.subheader("🏢 Top Hiring Companies")

    company_counts = df['company'].value_counts().head(10)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = plt.cm.Oranges(np.linspace(0.4, 0.9, len(company_counts)))
    ax.bar(company_counts.index, company_counts.values, color=colors)
    ax.set_xlabel('Company')
    ax.set_ylabel('Openings')
    ax.set_title('Top Hiring Companies')
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    st.pyplot(fig)


def show_salary_trends(df):
    """Salary analysis page"""
    st.header("Salary Trends Analysis")

    salaries = extract_salaries(df)

    if not salaries:
        st.warning("No salary data available in the dataset")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Average Salary", f"{np.mean(salaries):,.0f}")

    with col2:
        st.metric("Median Salary", f"{np.median(salaries):,.0f}")

    with col3:
        st.metric("Sample Size", f"{len(salaries):,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Salary Distribution")

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(salaries, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(salaries), color='red', linestyle='--',
                  label=f'Mean: {np.mean(salaries):,.0f}')
        ax.axvline(np.median(salaries), color='green', linestyle='--',
                  label=f'Median: {np.median(salaries):,.0f}')
        ax.set_xlabel('Salary')
        ax.set_ylabel('Frequency')
        ax.set_title('Salary Distribution Histogram')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Salary Box Plot")

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.boxplot(salaries, vert=False, patch_artist=True,
                  boxprops=dict(facecolor='lightblue'))
        ax.set_xlabel('Salary')
        ax.set_title('Salary Distribution (Box Plot)')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)

    # Salary by skill
    st.markdown("---")
    st.subheader("💰 Salary by Top Skills")

    all_skills = [skill for skills in df['skills_extracted'].dropna() for skill in skills]
    top_skills = [s for s, _ in Counter(all_skills).most_common(10)]

    skill_salaries = {}
    for skill in top_skills:
        mask = df['skills_extracted'].apply(lambda x: skill in x if isinstance(x, list) else False)
        skill_df = df[mask]
        skill_sals = extract_salaries(skill_df)
        if skill_sals:
            skill_salaries[skill] = np.mean(skill_sals)

    if skill_salaries:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.RdYlBu(np.linspace(0.2, 0.8, len(skill_salaries)))
        ax.bar(skill_salaries.keys(), skill_salaries.values(), color=colors)
        ax.set_xlabel('Skill')
        ax.set_ylabel('Average Salary')
        ax.set_title('Average Salary by Skill')
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        st.pyplot(fig)


def show_upload_page():
    """Data upload page"""
    st.header("Upload Job Data")

    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")

            st.subheader("Preview")
            st.dataframe(df.head(), use_container_width=True)

            st.subheader("Data Info")
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Rows:** {len(df):,}")
                st.write(f"**Columns:** {len(df.columns)}")

            with col2:
                st.write(f"**Columns:** {', '.join(df.columns.tolist())}")

            # Save to data folder
            save_path = os.path.join('data', 'jobs_data_latest.csv')
            os.makedirs('data', exist_ok=True)
            df.to_csv(save_path, index=False)
            st.success(f"Data saved to {save_path}")

        except Exception as e:
            st.error(f"Error processing file: {e}")

    st.markdown("---")
    st.subheader("Expected CSV Format")
    st.code("""
Required columns:
- title: Job title
- company: Company name
- location: Job location
- salary: Salary information
- description: Job description
- skills_extracted: List of extracted skills (as string representation of list)
- scraped_date: Date when job was scraped
- source: Source portal name
    """)


if __name__ == "__main__":
    main()
