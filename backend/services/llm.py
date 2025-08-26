# backend/services/llm.py
import os
import pathlib
from dotenv import load_dotenv

# --- figure out paths ---
# this file = backend/services/llm.py
SERVICES_DIR = pathlib.Path(__file__).resolve().parent                      # .../backend/services
BACKEND_DIR  = SERVICES_DIR.parent                                          # .../backend
ROOT_DIR     = BACKEND_DIR.parent                                           # repo root

CANDIDATE_ENVS = [
    ROOT_DIR / ".env",                   # <repo>/.env   (RECOMMENDED)
    BACKEND_DIR / ".env",                # <repo>/backend/.env
    SERVICES_DIR / ".env",               # <repo>/backend/services/.env
]

# Load in order (earlier wins). override=False means an earlier load won't be overwritten
loaded = []
for p in CANDIDATE_ENVS:
    if p.exists():
        load_dotenv(p, override=False)
        loaded.append(str(p))

# --- Gemini setup ---
import google.generativeai as genai  # noqa: E402

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# DEBUG: show what we tried and whether we found the key
print(
    "LLM .env debug\n  tried:", " | ".join(str(p) for p in CANDIDATE_ENVS),
    "\n  loaded:", loaded or "(none loaded)",
    "\n  has GEMINI_API_KEY:", bool(API_KEY),
    "\n  model:", MODEL,
    flush=True,
)

if not API_KEY or API_KEY == "your_gemini_api_key_here":
    print("⚠️  WARNING: GEMINI_API_KEY is missing or placeholder!")
    print("📝 To use AI features, please:")
    print("   1. Get your API key from: https://makersuite.google.com/app/apikey")
    print("   2. Set environment variable: GEMINI_API_KEY=your_key_here")
    print("   3. Or create a .env file in project root")
    print("🔧 Running in demo mode without AI features...")
    
    # Set flag for demo mode
    API_KEY = None

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        print("✅ Gemini AI configured successfully")
    except Exception as e:
        print(f"🚨 Failed to configure Gemini AI: {e}")
        API_KEY = None

def generate_text(prompt: str) -> str:
    """Return a plain text response from Gemini; never raise."""
    if not prompt or not prompt.strip():
        return "Error: Empty prompt provided"
    
    if not API_KEY:
        return "🔧 Demo Mode: AI features disabled. Please set GEMINI_API_KEY to enable AI responses."
    
    try:
        model = genai.GenerativeModel(MODEL)
        resp = model.generate_content(prompt)
        
        if not resp or not hasattr(resp, 'text'):
            return "Error: Invalid response from Gemini API"
            
        result = (resp.text or "").strip()
        return result if result else "Error: Empty response from Gemini API"
        
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg:
            return "Error: Invalid Gemini API key. Please check your GEMINI_API_KEY in .env file"
        elif "quota" in error_msg.lower():
            return "⚠️ **LLM Quota Exceeded**: Unable to generate AI-powered responses. Using personalized fallback system."
        else:
            return f"LLM error: {error_msg}"

def get_llm_client():
    """Return a configured Gemini client for use in agents"""
    if not API_KEY:
        # Return a mock client for demo mode
        class MockClient:
            def generate_content(self, prompt):
                class MockResponse:
                    text = "🔧 Demo Mode: AI features disabled. Please set GEMINI_API_KEY to enable personalized responses."
                return MockResponse()
        return MockClient()
    
    try:
        return genai.GenerativeModel(MODEL)
    except Exception as e:
        raise RuntimeError(f"Failed to create Gemini client: {e}")
