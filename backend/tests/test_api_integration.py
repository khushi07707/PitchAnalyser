import time
import os
import wave
import struct
import math
import requests

BASE_URL = "http://127.0.0.1:8000/api"

def create_dummy_wav(filepath: str, duration_sec: float = 3.0):
    """Programmatically generate a standard 16kHz mono WAV file."""
    sample_rate = 16000
    num_samples = int(duration_sec * sample_rate)
    
    # Standard PCM 16-bit parameters
    with wave.open(filepath, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Generate 440Hz sound wave
        for i in range(num_samples):
            value = int(32767 * math.sin(2 * math.pi * 440 * i / sample_rate))
            wav_file.writeframes(struct.pack('h', value))
            
    print(f"Generated dummy WAV file: {filepath} ({duration_sec} seconds)")

def run_integration_test():
    print("====================================================")
    print("   AI Pitch Analyser End-to-End API Integration Test ")
    print("====================================================\n")
    
    dummy_file = "integration_test_sample.wav"
    create_dummy_wav(dummy_file, duration_sec=5.0)
    
    # 1. Register a test user
    print("\n[Step 1] Registering a new user...")
    email = f"tester_{int(time.time())}@pitchpilot.ai"
    reg_payload = {
        "email": email,
        "password": "SecurePassword123",
        "full_name": "QA Tester",
        "company": "QA Corporation",
        "role": "founder"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    if r.status_code != 201:
        print(f"FAILED to register: {r.status_code} {r.text}")
        return
    print(f"Success: Registered user {email}")
    
    # 2. Login to get JWT Token
    print("\n[Step 2] Logging in to retrieve JWT Auth token...")
    login_payload = {
        "email": email,
        "password": "SecurePassword123"
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if r.status_code != 200:
        print(f"FAILED to login: {r.status_code} {r.text}")
        return
    token_data = r.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Success: JWT access token obtained.")

    # 3. Test GET /me
    print("\n[Step 3] Fetching logged-in user profile details (/me)...")
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Me Response: {r.status_code} -> {r.json()}")
    
    # 4. Upload Recording
    print("\n[Step 4] Uploading dummy audio file...")
    with open(dummy_file, "rb") as f:
        files = {"file": (dummy_file, f, "audio/wav")}
        r = requests.post(f"{BASE_URL}/uploads/upload", files=files, headers=headers)
    if r.status_code != 201:
        print(f"FAILED to upload: {r.status_code} {r.text}")
        return
    upload_data = r.json()
    upload_id = upload_data["id"]
    print(f"Success: File uploaded. ID: {upload_id} | Status: {upload_data['status']}")
    
    # 5. Trigger Analysis (Background pipeline)
    print("\n[Step 5] Triggering speech & AI analysis pipeline...")
    r = requests.post(f"{BASE_URL}/analysis/process/{upload_id}", headers=headers)
    if r.status_code != 202:
        print(f"FAILED to trigger analysis: {r.status_code} {r.text}")
        return
    print("Success: Analysis processing started in the background.")
    
    # 6. Poll status until completed
    print("\n[Step 6] Polling processing status...")
    status = "pending"
    for attempt in range(15):
        r = requests.get(f"{BASE_URL}/analysis/status/{upload_id}", headers=headers)
        status_data = r.json()
        status = status_data["status"]
        print(f"   Poll #{attempt+1}: Status is '{status}'")
        if status in ["completed", "failed"]:
            break
        time.sleep(1.5)
        
    if status != "completed":
        print(f"Pipeline failed to complete. Final status: {status}")
        return
    print("Success: Analysis pipeline completed processing.")
    
    # 7. Query Report History
    print("\n[Step 7] Listing reports history...")
    r = requests.get(f"{BASE_URL}/reports", headers=headers)
    history = r.json()
    print(f"History list: {r.status_code} | Total items: {history['total']}")
    report_id = history["items"][0]["report_id"]
    
    # 8. Query Report Detail
    print("\n[Step 8] Fetching full report analytics detail...")
    r = requests.get(f"{BASE_URL}/reports/{report_id}", headers=headers)
    detail = r.json()
    print(f"Scores calculated: {detail['scores']}")
    print(f"Audio DSP metrics: {detail['analysis']['speaking_rate']} WPM | Pitch: {detail['analysis']['pitch_mean']}Hz | Style: {detail['analysis']['speaking_style']}")
    print(f"NLP characteristics: filler words count = {sum(detail['analysis']['filler_words'].values())}")
    
    # 9. Query Dashboard metrics
    print("\n[Step 9] Requesting dashboard metrics...")
    r_stats = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    r_user = requests.get(f"{BASE_URL}/dashboard/user-stats", headers=headers)
    print(f"Stats Card: {r_stats.json()}")
    print(f"Scores Averages: {r_user.json()}")
    
    # Cleanup dummy file
    if os.path.exists(dummy_file):
        os.remove(dummy_file)
        
    print("\n====================================================")
    print("   INTEGRATION TEST PASSED SUCCESSFULLY (100% OK)   ")
    print("====================================================")

if __name__ == "__main__":
    # Ensure backend server is running on localhost port 8000 before executing
    run_integration_test()
