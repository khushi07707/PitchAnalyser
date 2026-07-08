import os
import time
import requests
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuration
BASE_URL = "http://localhost:5183"

def create_sample_pdf(filename):
    """Creates a structurally valid PDF file containing sample pitch content."""
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, "AI Augmented Pitch Analyzer - Sample Pitch Deck")
    c.drawString(100, 720, "Company Name: TechNovation AI")
    c.drawString(100, 700, "Problem Statement:")
    c.drawString(100, 680, "Founders struggle to practice and refine their startup presentations.")
    c.drawString(100, 660, "Solution: An interactive AI tool that reviews deck slide text and transcript audio.")
    c.drawString(100, 640, "Market Size: Over $10 Billion global presentation coaching market.")
    c.drawString(100, 620, "Business Model: Subscription SaaS for incubators and university accelerators.")
    c.save()
    print(f"Generated valid PDF pitch deck: {filename}")

def run_tests():
    print("====================================================")
    print("   C# API End-to-End Integration Test Tool")
    print("====================================================")

    # 0. Prep PDF file
    os.makedirs("tests", exist_ok=True)
    pdf_filename = "tests/csharp_pitch_sample.pdf"
    create_sample_pdf(pdf_filename)

    email = f"csharp_tester_{random.randint(1000, 9999)}@pitchpilot.ai"
    password = "SecurePassword123!"
    headers = {}

    # 1. Register
    print("\n[Step 1] Registering user...")
    register_payload = {
        "firstName": "Developer",
        "lastName": "QA",
        "email": email,
        "password": password
    }
    r = requests.post(f"{BASE_URL}/api/Auth/register", json=register_payload)
    if r.status_code not in (200, 201):
        print(f"Error Registering: {r.status_code} | {r.text}")
        return False
    print(f"Success: Registered {email}")

    # 2. Login
    print("\n[Step 2] Logging in...")
    login_payload = {
        "email": email,
        "password": password
    }
    r = requests.post(f"{BASE_URL}/api/Auth/login", json=login_payload)
    if r.status_code != 200:
        print(f"Error Logging In: {r.status_code} | {r.text}")
        return False
    
    token = r.json().get("token")
    if not token:
        print("Error: JWT Token not found in response!")
        return False
    print("Success: JWT token acquired.")
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Startup
    print("\n[Step 3] Creating a startup...")
    startup_payload = {
        "name": "TechNovation AI",
        "founderName": "Developer QA",
        "founderEmail": email,
        "industry": 0, # Software
        "fundingStage": 1, # Pre-seed
        "businessDescription": "Building generative AI-driven tools for elevator pitch practices.",
        "websiteUrl": "https://technovation.ai"
    }
    r = requests.post(f"{BASE_URL}/api/Startups", json=startup_payload, headers=headers)
    if r.status_code not in (200, 201):
        print(f"Error Creating Startup: {r.status_code} | {r.text}")
        return False
    
    startup_data = r.json().get("data", {})
    startup_id = startup_data.get("id")
    print(f"Success: Startup created with ID: {startup_id}")

    # 4. Upload Pitch Deck
    print("\n[Step 4] Uploading PDF Pitch Deck...")
    with open(pdf_filename, "rb") as f:
        files = {
            "File": (os.path.basename(pdf_filename), f, "application/pdf")
        }
        data = {
            "StartupId": startup_id,
            "Title": "TechNovation Pitch Deck v1"
        }
        r = requests.post(f"{BASE_URL}/api/Pitch/upload", data=data, files=files, headers=headers)
    
    if r.status_code not in (200, 201):
        print(f"Error Uploading: {r.status_code} | {r.text}")
        return False
    
    pitch_data = r.json().get("data", {})
    pitch_id = pitch_data.get("id")
    print(f"Success: Pitch deck uploaded. Pitch ID: {pitch_id}")

    # 5. Trigger AI Analysis
    print("\n[Step 5] Triggering Pitch Analysis...")
    r = requests.post(f"{BASE_URL}/api/PitchAnalysis/{pitch_id}/analyze", headers=headers)
    if r.status_code != 200:
        print(f"Error Analyzing: {r.status_code} | {r.text}")
        return False
    
    analysis_data = r.json().get("data", {})
    print(f"Success: AI Analysis completed. Score: {analysis_data.get('score')}")
    print(f"Summary: {analysis_data.get('summary')}")
    print(f"Recommendations: {analysis_data.get('recommendations')}")

    # 6. Fetch Dashboard Stats
    print("\n[Step 6] Retrieving Dashboard...")
    r = requests.get(f"{BASE_URL}/api/PitchAnalysis/dashboard", headers=headers)
    if r.status_code != 200:
        print(f"Error fetching dashboard: {r.status_code} | {r.text}")
        return False
    print(f"Success: Dashboard stats -> {r.json().get('data')}")

    # 7. Fetch Analysis History
    print("\n[Step 7] Retrieving History...")
    r = requests.get(f"{BASE_URL}/api/PitchAnalysis/history", headers=headers)
    if r.status_code != 200:
        print(f"Error fetching history: {r.status_code} | {r.text}")
        return False
    print(f"Success: History item count: {len(r.json().get('data', []))}")

    print("\n====================================================")
    print("   C# BACKEND VERIFICATION PASSED SUCCESSFULLY! (100% OK)")
    print("====================================================")
    
    # Cleanup sample
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)
        
    return True

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"Test failed with exception: {e}")
