"""
FastAPI Backend for Real-Time Job Analytics
Provides REST API for the dashboard and external clients
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import os
from datetime import datetime
from collections import Counter
import json

app = FastAPI(
    title="Job Analytics API",
    description="Real-time job market analytics API",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobSearchRequest(BaseModel):
    keywords: str
    location: Optional[str] = ""
    limit: Optional[int] = 100


class JobResponse(BaseModel):
    title: str
    company: str
    location: str
    salary: str
    skills: List[str]
    source: str
    scraped_date: str


@app.get("/")
def read_root():
    return {
        "message": "Job Analytics API",
        "version": "1.0.0",
        "endpoints": [
            "/api/jobs",
            "/api/jobs/search",
            "/api/skills",
            "/api/locations",
            "/api/salaries",
            "/api/refresh"
        ]
    }


@app.get("/api/jobs", response_model=List[JobResponse])
def get_jobs(limit: int = 50):
    """Get latest job listings"""
    try:
        df = pd.read_csv('data/jobs_data_latest.csv')
        jobs = df.head(limit).to_dict('records')
        return jobs
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No job data available")


@app.post("/api/jobs/search")
def search_jobs(request: JobSearchRequest):
    """Search and scrape new jobs"""
    from scraper.realtime_scraper import RealTimeJobScraper

    scraper = RealTimeJobScraper()
    df = scraper.scrape_all_sources(request.keywords, request.location, request.limit)

    if not df.empty:
        scraper.save_to_csv(df)

    return {
        "count": len(df),
        "jobs": df.to_dict('records')
    }


@app.get("/api/skills")
def get_top_skills(limit: int = 20):
    """Get top in-demand skills"""
    try:
        df = pd.read_csv('data/jobs_data_latest.csv')
        all_skills = [skill for skills in df['skills_extracted'].dropna() for skill in skills]
        skill_counts = Counter(all_skills).most_common(limit)

        total_jobs = len(df)
        return [
            {
                "skill": skill,
                "count": count,
                "percentage": round(count / total_jobs * 100, 2) if total_jobs > 0 else 0
            }
            for skill, count in skill_counts
        ]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No job data available")


@app.get("/api/locations")
def get_location_stats():
    """Get job demand by location"""
    try:
        df = pd.read_csv('data/jobs_data_latest.csv')
        location_counts = df['location'].value_counts().head(15).to_dict()

        total_jobs = len(df)
        return [
            {
                "location": loc,
                "count": count,
                "percentage": round(count / total_jobs * 100, 2) if total_jobs > 0 else 0
            }
            for loc, count in location_counts.items()
        ]
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No job data available")


@app.get("/api/salaries")
def get_salary_stats(skill: Optional[str] = None):
    """Get salary statistics"""
    import re

    try:
        df = pd.read_csv('data/jobs_data_latest.csv')

        if skill:
            mask = df['skills_extracted'].apply(
                lambda x: skill in str(x) if pd.notna(x) else False
            )
            df = df[mask]

        salaries = []
        for salary in df['salary'].dropna():
            numbers = re.findall(r'\d+', str(salary))
            if numbers:
                avg = sum(float(n) for n in numbers[:2]) / len(numbers[:2])
                salaries.append(avg)

        if not salaries:
            return {"message": "No salary data available"}

        import numpy as np
        return {
            "average": float(np.mean(salaries)),
            "median": float(np.median(salaries)),
            "min": float(np.min(salaries)),
            "max": float(np.max(salaries)),
            "sample_size": len(salaries)
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No job data available")


@app.get("/api/refresh")
def refresh_data(keywords: str = "Python developer", location: str = ""):
    """Force refresh job data"""
    from scraper.realtime_scraper import RealTimeJobScraper

    scraper = RealTimeJobScraper()
    df = scraper.scrape_all_sources(keywords, location)

    if not df.empty:
        scraper.save_to_csv(df)
        return {
            "status": "success",
            "jobs_scraped": len(df),
            "timestamp": datetime.now().isoformat()
        }

    return {
        "status": "no_data",
        "message": "No jobs found"
    }


@app.get("/api/stats")
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    try:
        df = pd.read_csv('data/jobs_data_latest.csv')

        all_skills = [skill for skills in df['skills_extracted'].dropna() for skill in skills]
        skill_counts = Counter(all_skills).most_common(10)

        return {
            "total_jobs": len(df),
            "unique_companies": df['company'].nunique(),
            "unique_locations": df['location'].nunique(),
            "sources": df['source'].unique().tolist() if 'source' in df.columns else [],
            "top_skills": [
                {"skill": s, "count": c} for s, c in skill_counts
            ],
            "last_updated": datetime.now().isoformat()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No job data available")


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("    JOB ANALYTICS API SERVER")
    print("=" * 60)
    print("\nStarting API server on http://localhost:8000")
    print("\nAvailable endpoints:")
    print("  GET  /api/jobs          - Get job listings")
    print("  POST /api/jobs/search   - Search & scrape jobs")
    print("  GET  /api/skills        - Get top skills")
    print("  GET  /api/locations     - Get location stats")
    print("  GET  /api/salaries      - Get salary data")
    print("  GET  /api/refresh       - Refresh job data")
    print("  GET  /api/stats         - Dashboard stats")
    print("\nAPI Docs: http://localhost:8000/docs")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)
