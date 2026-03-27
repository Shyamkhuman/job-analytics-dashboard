# Job Market Analytics Platform

A smart analytics platform that gathers job postings from various online sources and analyzes trending skills, technologies, and roles based on user's field of interest.

## Features

- **Web Scraping**: Collects job data from multiple portals (Indeed, Naukri, etc.)
- **Skills Analysis**: Identifies trending skills and roles in specific fields
- **Data Visualization**: Creates charts for salary trends, skills demand, and market patterns
- **Interactive Dashboard**: Streamlit web app for exploring personalized job market insights

## Project Structure

```
job_analytics_platform/
├── scraper/
│   └── job_scraper.py      # Web scraping module
├── analyzer/
│   └── skills_analyzer.py  # Data analysis module
├── visualization/
│   └── charts.py           # Visualization module
├── dashboard/
│   └── app.py              # Streamlit dashboard
├── data/                   # Stored job data and analysis results
├── outputs/
│   └── charts/             # Generated visualizations
├── requirements.txt        # Python dependencies
└── README.md
```

## Installation

1. **Clone or navigate to the project folder:**
   ```bash
   cd job_analytics_platform
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Scrape Job Data

Run the web scraper to collect job postings:

```bash
python scraper/job_scraper.py
```

Enter your job keywords (e.g., "Python developer", "data scientist") and location when prompted.

### 2. Analyze the Data

Run the skills analyzer:

```bash
python analyzer/skills_analyzer.py
```

This generates insights about:
- Top in-demand skills
- Skills by category
- Experience level breakdown
- Salary analysis

### 3. Generate Visualizations

Create charts and graphs:

```bash
python visualization/charts.py
```

Charts are saved to `outputs/charts/`

### 4. Launch the Dashboard

Start the interactive Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Dashboard Features

- **Dashboard**: Overview of key metrics and top skills
- **Skills Analysis**: Detailed breakdown by category and correlations
- **Location Insights**: Geographic demand analysis
- **Salary Trends**: Salary distribution and comparison by skill
- **Upload Data**: Upload your own CSV job data

## SDG Alignment

This project supports:

- **SDG 4 - Quality Education**: Helps students understand required skills and align learning with industry needs
- **SDG 8 - Decent Work and Economic Growth**: Supports employment awareness and career planning based on market demand
- **SDG 9 - Industry, Innovation and Infrastructure**: Promotes digital platforms that analyze workforce trends

## Technologies Used

- **Python** - Core programming language
- **BeautifulSoup/Scrapy** - Web scraping
- **Pandas/NumPy** - Data analysis
- **Matplotlib/Seaborn** - Data visualization
- **Streamlit** - Web dashboard framework
- **Scikit-learn** - Machine learning (for trend prediction)

## Configuration

Create a `.env` file for API keys (optional):

```
INDEED_API_KEY=your_key_here
LINKEDIN_API_KEY=your_key_here
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

---

**Built for students and professionals to make data-driven career decisions**
