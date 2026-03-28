"""
Job Analytics Platform - Main Entry Point
Run the complete pipeline: scrape → analyze → visualize → dashboard
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 60)
    print("       JOB MARKET ANALYTICS PLATFORM")
    print("=" * 60)
    print()

    # Step 1: Scrape
    print("STEP 1: Real-Time Web Scraping")
    print("-" * 40)

    from scraper.realtime_scraper import RealTimeJobScraper

    keywords = input("Enter job keywords to search: ").strip()
    if not keywords:
        keywords = "Python developer"
        print(f"Using default: {keywords}")

    location = input("Enter location (or press Enter for global): ").strip()
    
    count_input = input("How many jobs to scrape/generate? (default 1000): ").strip()
    try:
        limit = int(count_input) if count_input else 1000
    except ValueError:
        limit = 1000

    scraper = RealTimeJobScraper()
    print(f"\nStarting job search for '{keywords}' in '{location or 'Global'}'...")

    df = scraper.scrape_all_sources(keywords, location, limit=limit)

    if df.empty:
        print("\n⚠️  No jobs found. Check your internet connection or try different keywords.")
        return

    print(f"\n✅ Scraped/Generated {len(df)} jobs")

    # Save data
    os.makedirs('data', exist_ok=True)
    filename = f"data/jobs_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"💾 Data saved to {filename}")

    # Also save as 'latest' for easy access
    df.to_csv('data/jobs_data_latest.csv', index=False)

    # Step 2: Analyze
    print("\n" + "=" * 60)
    print("STEP 2: Data Analysis")
    print("-" * 40)

    from analyzer.skills_analyzer import SkillsAnalyzer

    analyzer = SkillsAnalyzer(df)
    insights = analyzer.generate_insights()

    print(f"\n📊 Analysis Summary:")
    print(f"   Total Jobs: {insights['summary']['total_jobs_analyzed']:,}")
    print(f"   Unique Companies: {insights['summary']['unique_companies']:,}")
    print(f"   Unique Locations: {insights['summary']['unique_locations']:,}")

    print(f"\n🔥 Top 10 Skills:")
    for i, skill in enumerate(insights['top_skills'][:10], 1):
        print(f"   {i}. {skill['skill']}: {skill['demand_count']} jobs ({skill['percentage']}%)")

    # Export analysis
    analyzer.export_analysis('data/analysis_results.json')

    # Step 3: Visualize
    print("\n" + "=" * 60)
    print("STEP 3: Data Visualization")
    print("-" * 40)

    from visualization.charts import JobMarketVisualizer

    visualizer = JobMarketVisualizer(df)
    visualizer.create_all_charts()

    # Step 4: Dashboard
    print("\n" + "=" * 60)
    print("STEP 4: Launch Dashboard")
    print("-" * 40)

    print("\n✅ Pipeline complete!")
    print("\nTo launch the interactive dashboard, run:")
    print("   streamlit run dashboard/realtime_app.py")
    print("\nOr view the generated charts in: outputs/charts/")

    # Auto-launch option
    launch = input("\nLaunch dashboard now? (y/n): ").strip().lower()
    if launch == 'y':
        import subprocess
        subprocess.run(['streamlit', 'run', 'dashboard/realtime_app.py'])


if __name__ == "__main__":
    main()
