"""
Streamlit Dashboard with Real-Time Updates and Resume Matching
Auto-refreshing job analytics dashboard with resume upload feature
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os
import re
from datetime import datetime
import json
import sys
import ast

# Page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="Real-Time Job Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robust path handling to find project root and scraper
try:
    # Get the directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root (job_analytics_platform)
    project_root = os.path.dirname(current_dir)
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    # Test if scraper is accessible
    from scraper.realtime_scraper import RealTimeJobScraper
except ImportError as e:
    st.error(f"⚠️ Critical Error: Could not load the scraper module. {e}")
    st.info(f"Debug Info - Current Dir: {os.getcwd()} | Script Dir: {current_dir} | Project Root: {project_root}")
    st.stop()

# Get absolute paths for data
DATA_PATH = os.path.join(project_root, 'data', 'jobs_data_latest.csv')
RESUME_DIR = os.path.join(project_root, 'resumes')
os.makedirs(RESUME_DIR, exist_ok=True)

# Custom CSS
st.markdown("""
<style>
    .sidebar-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
        line-height: 1.0;
        letter-spacing: -0.5px;
    }
    .sidebar-live {
        color: #10b981;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    .job-card {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
    .job-card h4 {
        color: inherit !important;
    }
    .job-card p {
        color: inherit !important;
        opacity: 0.8;
    }
    .match-score {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .skill-focus-card {
        text-align: center;
        padding: 10px;
        background: rgba(128, 128, 128, 0.1);
        border-radius: 10px;
    }
    .skill-focus-card span {
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def load_data() -> pd.DataFrame:
    """Load the latest job data from CSV with a 1-minute cache"""
    try:
        # Check if the file exists and get modification time for sidebar
        if not os.path.exists(DATA_PATH):
            return None
            
        df = pd.read_csv(DATA_PATH)
        if 'skills_extracted' in df.columns:
            df['skills_extracted'] = df['skills_extracted'].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) and x != 'nan' else []
            )
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def extract_skills_from_text(text: str, skill_library: list = None) -> list:
    """Extract skills from resume or job description using improved regex"""
    default_library = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C\+\+', 'C#', 'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R',
        # Frontend
        'React', 'Angular', 'Vue', 'Next\.js', 'HTML5?', 'CSS3?', 'SASS', 'Tailwind', 'Bootstrap', 'jQuery', 'Webpack', 'Vite',
        # Backend & Frameworks
        'Node\.js', 'Django', 'Flask', 'FastAPI', 'Spring Boot', 'Express', '\.NET', 'ASP\.NET', 'Laravel', 'Rails', 'GraphQL', 'REST API',
        # Databases
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'Elasticsearch', 'Cassandra', 'DynamoDB', 'Firebase',
        # Cloud & DevOps
        'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Ansible', 'CI/CD', 'GitLab', 'GitHub Actions', 'Linux', 'Unix', 'Serverless', 'Microservices',
        # Data Science & AI
        'Machine Learning', 'Deep Learning', 'Artificial Intelligence', 'AI', 'NLP', 'Computer Vision', 'Data Analysis', 'Data Engineering',
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Keras', 'Pandas', 'NumPy', 'Matplotlib', 'Tableau', 'Power BI', 'Spark', 'Hadoop', 'Kafka',
        # Soft Skills & Management
        'Project Management', 'Agile', 'Scrum', 'Leadership', 'Teamwork', 'Communication', 'Problem Solving', 'Critical Thinking', 'Adaptability',
        'Strategic Planning', 'Time Management', 'Stakeholder Management', 'Public Speaking', 'Mentoring', 'Conflict Resolution',
        # Tools & Other
        'Git', 'Jira', 'Confluence', 'Figma', 'Adobe XD', 'Slack', 'Trello', 'Postman', 'Vagrant', 'CircleCI', 'Unity', 'Unreal Engine'
    ]
    
    # Merge provided library with default library
    if skill_library:
        # Clean the provided library (remove escapes if any)
        cleaned_provided = [s.replace('\\', '') for s in skill_library]
        combined_library = sorted(list(set(default_library + cleaned_provided)), key=len, reverse=True)
    else:
        combined_library = default_library

    found_skills = set()
    # Normalize text for better matching
    text = f" {text.replace('\\n', ' ')} "
    
    for skill in combined_library:
        # Use a more flexible boundary that handles spaces and special characters
        # Matches skill if preceded and followed by non-alphanumeric or start/end of string
        pattern = rf'(?i)(?<=[\s\W]){re.escape(skill.replace("\\", ""))}(?=[\s\W])'
        if re.search(pattern, text):
            found_skills.add(skill.replace('\\', ''))

    return sorted(list(found_skills))


def calculate_match_score(resume_skills: set, job_skills: set) -> float:
    """Calculate match score between resume and job requirements"""
    if not job_skills:
        return 0.0

    matching_skills = resume_skills.intersection(job_skills)
    
    # Calculate weighted base score
    # 70% of score is matching required skills
    base_score = (len(matching_skills) / len(job_skills)) * 80 if job_skills else 0

    # 20% bonus for additional relevant skills matched (scaled by job requirement complexity)
    bonus = min(len(matching_skills) * 3, 20)

    # Add a bit of randomness to make it feel "real-time" and dynamic (optional but can help user feedback)
    import random
    variation = random.uniform(-2, 2)
    
    final_score = base_score + bonus + variation
    return max(0, min(final_score, 100))


def match_resume_to_jobs(resume_text: str, df: pd.DataFrame, top_n: int = 10) -> list:
    """Match resume to jobs and return ranked recommendations"""
    # Create a skill library from all skills in the dataset
    all_known_skills = set()
    for skills_list in df['skills_extracted'].dropna():
        if isinstance(skills_list, list):
            for skill in skills_list:
                all_known_skills.add(re.escape(skill))
    
    # Extract skills from resume using known skills as library
    resume_skills = set(extract_skills_from_text(resume_text, skill_library=list(all_known_skills)))

    job_matches = []
    for idx, row in df.iterrows():
        job_skills = set(row.get('skills_extracted', []))
        score = calculate_match_score(resume_skills, job_skills)

        # Only include if there's at least some match or if it's highly relevant
        if score > 0:
            job_matches.append({
                'match_score': round(score, 1),
                'title': row.get('title', ''),
                'company': row.get('company', ''),
                'location': row.get('location', ''),
                'salary': row.get('salary', ''),
                'skills': list(job_skills),
                'matching_skills': list(resume_skills.intersection(job_skills)),
                'missing_skills': list(job_skills - resume_skills),
                'source': row.get('source', ''),
                'description': row.get('description', '')
            })

    # Sort by match score descending, then by number of matching skills
    job_matches.sort(key=lambda x: (x['match_score'], len(x['matching_skills'])), reverse=True)
    return job_matches[:top_n]


def extract_skills_from_resume(file) -> str:
    """Extract text from uploaded resume (PDF or TXT)"""
    file_type = file.name.lower().split('.')[-1]

    if file_type == 'txt':
        return file.read().decode('utf-8')
    elif file_type == 'pdf':
        try:
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except:
            # Fallback: try pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text()
                return text
            except:
                st.warning("PDF parsing failed. Please ensure the PDF is not password-protected or try a TXT file.")
                return file.read().decode('utf-8', errors='ignore')
    else:
        return file.read().decode('utf-8', errors='ignore')


# Sidebar
st.sidebar.markdown('<p class="sidebar-header">Job Analysis Platform</p>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-live">LIVE SYSTEM</div>', unsafe_allow_html=True)

st.sidebar.header("Dashboard Controls")

# Navigation
page = st.sidebar.radio(
    "Navigate:",
    ["Dashboard", "Skills Analysis", "Locations", "Salary Trends", "Resume Matcher", "Total Job Posts"],
    index=0
)

# Data info
df = load_data()
if df is not None and not df.empty:
    st.sidebar.success(f"{len(df)} jobs loaded")
    # Show the actual modification time of the data file
    if os.path.exists(DATA_PATH):
        mtime = os.path.getmtime(DATA_PATH)
        last_modified = datetime.fromtimestamp(mtime).strftime('%H:%M:%S')
        st.sidebar.caption(f"Data last updated: {last_modified}")
    else:
        st.sidebar.caption(f"Last checked: {datetime.now().strftime('%H:%M:%S')}")

# Generation buttons
st.sidebar.markdown("---")
st.sidebar.subheader("Generate Fresh Data")

if st.sidebar.button("Generate 100 Global Jobs", use_container_width=True):
    with st.sidebar.status("Generating 100 jobs..."):
        scraper = RealTimeJobScraper()
        new_df = scraper.scrape_all_sources("Python", limit=100)
        scraper.save_to_csv(new_df)
        st.cache_data.clear()
        st.sidebar.success("100 Jobs Generated!")
        st.rerun()

if st.sidebar.button("Generate 500 Global Jobs", use_container_width=True):
    with st.sidebar.status("Generating 500 jobs..."):
        scraper = RealTimeJobScraper()
        new_df = scraper.scrape_all_sources("Python", limit=500)
        scraper.save_to_csv(new_df)
        st.cache_data.clear()
        st.sidebar.success("500 Jobs Generated!")
        st.rerun()

if st.sidebar.button("All Available Jobs", use_container_width=True):
    with st.sidebar.status("Performing deep scan..."):
        scraper = RealTimeJobScraper()
        new_df = scraper.scrape_all_sources("Python", limit=2500)
        scraper.save_to_csv(new_df)
        st.cache_data.clear()
        st.sidebar.success(f"Deep scan complete: {len(new_df)} jobs found!")
        st.rerun()

# Refresh View
if st.sidebar.button("Refresh Dashboard View", use_container_width=True):
    st.cache_data.clear()
    st.toast("Refreshing data...")
    st.rerun()

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.info("""
### Features
- Real-time analytics
- Live job scraping
- Resume matching
- Skill recommendations
""")


# ============= DASHBOARD PAGE =============
if page == "Dashboard":
    st.header("Market Overview")

    if df is None or df.empty:
        st.warning("No data available. Please upload data or run the scraper.")
        st.stop()

    # Key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Jobs", f"{len(df):,}")

    with col2:
        st.metric("Companies", f"{df['company'].nunique():,}")

    with col3:
        st.metric("Locations", f"{df['location'].nunique():,}")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Top 15 In-Demand Skills")

        all_skills = [skill for skills in df['skills_extracted'].dropna() for skill in skills]
        skill_counts = Counter(all_skills).most_common(15)

        skills_df = pd.DataFrame(skill_counts, columns=['Skill', 'Count'])

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(skills_df)))
        bars = ax.barh(skills_df['Skill'], skills_df['Count'], color=colors)
        ax.set_xlabel('Job Postings')
        ax.invert_yaxis()

        for bar, count in zip(bars, skills_df['Count']):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(int(count)), va='center', fontsize=9)

        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Experience Distribution")

        experience_keywords = {
            'Entry': ['fresher', 'entry level', 'junior', 'trainee', '0-2 years'],
            'Mid': ['mid level', 'mid-level', '2-5 years', '3-5 years'],
            'Senior': ['senior', 'lead', 'principal', '5+ years', 'manager'],
        }

        exp_counts = {}
        for level, keywords in experience_keywords.items():
            mask = df['title'].str.lower().str.contains('|'.join(keywords), na=False)
            exp_counts[level] = int(mask.sum())
        exp_counts['Other'] = len(df) - sum(exp_counts.values())

        fig, ax = plt.subplots(figsize=(6, 6))
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(exp_counts)))
        ax.pie(exp_counts.values(), labels=exp_counts.keys(), autopct='%1.1f%%',
              colors=colors, explode=[0.02]*len(exp_counts))
        plt.tight_layout()
        st.pyplot(fig)

    # Recent jobs
    st.markdown("---")
    st.subheader("Latest Job Postings")

    display_cols = ['title', 'company', 'location', 'salary', 'source', 'scraped_date']
    available_cols = [c for c in display_cols if c in df.columns]
    display_df = df[available_cols].head(10)
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ============= SKILLS ANALYSIS PAGE =============
elif page == "Skills Analysis":
    st.header("Skills Deep Dive")

    if df is None or df.empty:
        st.warning("No data available.")
        st.stop()

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

    selected_category = st.selectbox("Select Category", list(categories.keys()))

    cat_skills = [(s, skill_counts.get(s, 0)) for s in categories[selected_category]
                  if skill_counts.get(s, 0) > 0]
    cat_skills.sort(key=lambda x: x[1], reverse=True)

    if cat_skills:
        cat_df = pd.DataFrame(cat_skills, columns=['Skill', 'Demand'])

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(cat_df)))
        ax.bar(cat_df['Skill'], cat_df['Demand'], color=colors)
        ax.set_title(f'{selected_category} - Demand Analysis')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

        st.dataframe(cat_df, use_container_width=True, hide_index=True)

    # Skill correlation
    st.markdown("---")
    st.subheader("Skill Co-occurrence Matrix")

    top_n = st.slider("Number of skills to analyze", 5, 20, 10)
    top_skills = [s for s, _ in skill_counts.most_common(top_n)]

    if top_skills:
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


# ============= LOCATION INSIGHTS PAGE =============
elif page == "Locations":
    st.header("Geographic Insights")

    if df is None or df.empty:
        st.warning("No data available.")
        st.stop()

    # Location Filter
    all_locations = sorted(df['location'].unique().tolist())
    selected_locations = st.multiselect(
        "Select Locations to Analyze:",
        options=all_locations,
        default=[],
        help="Leave empty to see all locations"
    )

    # Apply filter
    if selected_locations:
        location_df = df[df['location'].isin(selected_locations)]
        st.info(f"Showing analysis for: {', '.join(selected_locations)}")
    else:
        location_df = df
        st.info("Showing analysis for all locations")

    location_counts = location_df['location'].value_counts().head(15)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Locations")

        if not location_counts.empty:
            fig, ax = plt.subplots(figsize=(8, 8))
            colors = plt.cm.Greens(np.linspace(0.3, 0.9, len(location_counts)))
            bars = ax.barh(location_counts.index, location_counts.values, color=colors)
            ax.set_xlabel('Job Postings')
            ax.invert_yaxis()

            for bar, count in zip(bars, location_counts.values):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                       str(int(count)), va='center', fontsize=9)

            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.write("No data available for selected locations")

    with col2:
        st.subheader("Location Statistics")

        if not location_counts.empty:
            loc_stats = pd.DataFrame({
                'Location': location_counts.index,
                'Jobs': location_counts.values,
                'Percentage': (location_counts.values / len(location_df) * 100).round(2)
            })
            st.dataframe(loc_stats, use_container_width=True, hide_index=True)
        else:
            st.write("No statistics available")

    st.markdown("---")
    st.subheader("Available Jobs in Selected Area")
    
    if not location_df.empty:
        # Select and rename columns for display
        display_jobs = location_df[['title', 'company', 'salary']].copy()
        st.dataframe(display_jobs, use_container_width=True, hide_index=True)
    else:
        st.write("No job listings available for selected locations")

    st.markdown("---")
    st.subheader("Top Hiring Companies")

    company_counts = location_df['company'].value_counts().head(10)

    if not company_counts.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.Oranges(np.linspace(0.4, 0.9, len(company_counts)))
        ax.bar(company_counts.index, company_counts.values, color=colors)
        ax.set_title(f"Top Hiring Companies in { 'Selected Locations' if selected_locations else 'All Locations'}")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write("No company data available for selected locations")


# ============= SALARY TRENDS PAGE =============
elif page == "Salary Trends":
    st.header("Salary Analysis")

    if df is None or df.empty:
        st.warning("No data available.")
        st.stop()

    salaries = []
    for salary in df['salary'].dropna():
        numbers = re.findall(r'\d+', str(salary))
        if numbers:
            avg = np.mean([float(n) for n in numbers[:2]])
            salaries.append(avg)

    if not salaries:
        st.warning("No salary data available in the dataset.")
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Average Salary", f"{np.mean(salaries):,.0f}")

    with col2:
        st.metric("Median Salary", f"{np.median(salaries):,.0f}")

    with col3:
        st.metric("Sample Size", f"{len(salaries):,}")

    st.markdown("---")

    # Salary by skill
    st.subheader("Salary by Top Skills")

    all_skills = [skill for skills in df['skills_extracted'].dropna() for skill in skills]
    top_skills = [s for s, _ in Counter(all_skills).most_common(10)]

    skill_salaries = {}
    for skill in top_skills:
        mask = df['skills_extracted'].apply(lambda x: skill in x if isinstance(x, list) else False)
        skill_df = df[mask]
        skill_sals = []
        for salary in skill_df['salary'].dropna():
            numbers = re.findall(r'\d+', str(salary))
            if numbers:
                avg = np.mean([float(n) for n in numbers[:2]])
                skill_sals.append(avg)
        if skill_sals:
            skill_salaries[skill] = np.mean(skill_sals)

    if skill_salaries:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = plt.cm.RdYlBu(np.linspace(0.2, 0.8, len(skill_salaries)))
        ax.bar(skill_salaries.keys(), skill_salaries.values(), color=colors)
        ax.set_title('Average Salary by Skill')
        ax.set_ylabel('Salary')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)


# ============= RESUME MATCHER PAGE =============
elif page == "Resume Matcher":
    st.header("Resume to Job Matcher")
    st.markdown("""
    Upload your resume to get personalized job recommendations.
    Our system will match your skills with available jobs and show you the best fits.
    """)

    if df is None or df.empty:
        st.warning("No job data available. Please load job data first.")
        st.stop()

    # Upload section
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'pdf'],
        help="Upload your resume in TXT or PDF format"
    )

    # Process resume
    resume_text = None

    if uploaded_file is not None:
        resume_text = extract_skills_from_resume(uploaded_file)
        st.success(f"Resume '{uploaded_file.name}' uploaded successfully!")

    if resume_text:
        st.markdown("---")

        # Create a skill library from all skills in the dataset for better extraction
        all_known_skills = set()
        for skills_list in df['skills_extracted'].dropna():
            if isinstance(skills_list, list):
                for skill in skills_list:
                    all_known_skills.add(re.escape(skill))

        # Extract and display skills
        st.subheader("2. Skills Detected from Your Resume")
        resume_skills = extract_skills_from_text(resume_text, skill_library=list(all_known_skills))

        if resume_skills:
            skills_cols = st.columns(4)
            for i, skill in enumerate(resume_skills):
                with skills_cols[i % 4]:
                    st.markdown(f"<span class='match-score' style='font-size: 0.8rem; padding: 3px 10px;'>{skill}</span>",
                               unsafe_allow_html=True)
        else:
            st.warning("No recognized skills found. Please ensure your resume contains technical skills.")

        st.markdown("---")

        # Match button
        st.subheader("3. Find Matching Jobs")

        if st.button("Find My Best Match Jobs", use_container_width=True, type="primary"):
            with st.spinner("Analyzing your resume and matching with jobs..."):
                job_matches = match_resume_to_jobs(resume_text, df, top_n=10)

                # Store matches in session state
                st.session_state['job_matches'] = job_matches

                if job_matches:
                    st.success(f"Found {len(job_matches)} matching jobs!")

        # Display matches
        if 'job_matches' in st.session_state and st.session_state['job_matches']:
            st.markdown("---")
            st.subheader("Your Top Job Recommendations")

            for i, job in enumerate(st.session_state['job_matches'], 1):
                # Match score color
                score = job['match_score']
                if score >= 80:
                    score_color = "green"
                elif score >= 50:
                    score_color = "orange"
                else:
                    score_color = "red"

                with st.container():
                    st.markdown(f"""
                    <div class="job-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0;">{i}. {job['title']}</h4>
                                <p style="margin: 5px 0;">
                                    <strong>{job['company']}</strong> | {job['location']} | {job['salary']}
                                </p>
                            </div>
                            <span class="match-score" style="background: {score_color};">{job['match_score']}% Match</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Expandable details
                    with st.expander(f"View details for {job['title']}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("**Matching Skills:**")
                            if job['matching_skills']:
                                for skill in job['matching_skills']:
                                    st.write(f"- {skill}")
                            else:
                                st.write("No matching skills found")

                        with col2:
                            st.markdown("**Skills to Learn:**")
                            if job['missing_skills']:
                                for skill in job['missing_skills']:
                                    st.write(f"- {skill}")
                            else:
                                st.write("You have all required skills!")

                        st.markdown(f"**Source:** {job['source']}")

            # Learning recommendations
            st.markdown("---")
            st.subheader("Skills to Focus On")

            # Aggregate missing skills from top matches
            all_missing = []
            for job in st.session_state['job_matches'][:5]:
                all_missing.extend(job['missing_skills'])

            if all_missing:
                missing_counts = Counter(all_missing).most_common(5)
                st.write("Based on your top matches, consider learning these skills:")

                cols = st.columns(5)
                for i, (skill, count) in enumerate(missing_counts):
                    with cols[i]:
                        st.markdown(f"""
                        <div class="skill-focus-card">
                            <strong>{skill}</strong><br>
                            <span>{count} jobs</span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("Your skills match well with current job requirements!")

# ============= TOTAL JOB POSTS PAGE =============
elif page == "Total Job Posts":
    st.header("All Job Postings")
    
    if df is None or df.empty:
        st.warning("No job data available. Please load job data first.")
        st.stop()

    # Search and Filter section
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("Search jobs by title, company, or location:", "")
    with col2:
        sort_order = st.selectbox("Sort by:", ["Newest First", "Oldest First", "Title (A-Z)"])

    # Apply search filter
    filtered_df = df.copy()
    if search_query:
        search_mask = (
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['company'].str.contains(search_query, case=False, na=False) |
            filtered_df['location'].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]

    # Apply sorting
    if sort_order == "Newest First":
        filtered_df = filtered_df.sort_values('scraped_date', ascending=False)
    elif sort_order == "Oldest First":
        filtered_df = filtered_df.sort_values('scraped_date', ascending=True)
    else:
        filtered_df = filtered_df.sort_values('title')

    # Display metrics for current view
    st.info(f"Showing {len(filtered_df)} of {len(df)} total jobs")

    # Column configuration for display
    display_cols = ['title', 'company', 'location', 'salary', 'source', 'scraped_date']
    # Add skills if they exist
    if 'skills_extracted' in filtered_df.columns:
        # Convert list to string for better display in dataframe
        display_df = filtered_df.copy()
        display_df['skills'] = display_df['skills_extracted'].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        display_cols.append('skills')
        st.dataframe(display_df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption(f"Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total jobs analyzed: {len(df) if df is not None else 0:,}")
