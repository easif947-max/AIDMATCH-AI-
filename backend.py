import os
import json
import sqlite3
import hashlib
from typing import Dict, List, Any
from groq import Groq

DB_FILE = "aidmatch.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table with Hashed Passwords
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        cnic TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Programs Catalog Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS programs (
        program_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        provider TEXT NOT NULL,
        eligibility_json TEXT NOT NULL,
        official_url TEXT NOT NULL,
        document_checklist TEXT NOT NULL,
        apply_pathway TEXT NOT NULL
    )
    """)

    # 3. Privacy-Isolated Search History (Linked directly to user_id)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        search_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category_searched TEXT NOT NULL,
        input_profile_json TEXT NOT NULL,
        eligible_program_ids TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# AUTHENTICATION & ISOLATED HISTORY
# ---------------------------------------------------------
def register_user(email: str, password: str, cnic: str, full_name: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO users (email, password_hash, cnic, full_name)
            VALUES (?, ?, ?, ?)
        """, (email.lower().strip(), hashed, cnic.strip(), full_name.strip()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"success": True, "user": {"user_id": user_id, "email": email, "cnic": cnic, "name": full_name}}
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "error": "An account with this Email or CNIC already exists."}

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("""
        SELECT user_id, email, cnic, full_name
        FROM users
        WHERE LOWER(email) = ? AND password_hash = ?
    """, (email.lower().strip(), hashed))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"success": True, "user": {"user_id": row["user_id"], "email": row["email"], "cnic": row["cnic"], "name": row["full_name"]}}
    return {"success": False, "error": "Invalid Email or Password."}

def save_search_history(user_id: int, category: str, profile: dict, matches: list):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO search_history (user_id, category_searched, input_profile_json, eligible_program_ids)
        VALUES (?, ?, ?, ?)
    """, (user_id, category, json.dumps(profile), json.dumps(matches)))
    conn.commit()
    conn.close()

def get_user_search_history(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT search_id, category_searched, input_profile_json, eligible_program_ids, timestamp
        FROM search_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            "search_id": row["search_id"],
            "category": row["category_searched"],
            "profile": json.loads(row["input_profile_json"]),
            "matches": json.loads(row["eligible_program_ids"]),
            "timestamp": row["timestamp"]
        })
    return history

def fetch_all_programs() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM programs")
    rows = cursor.fetchall()
    conn.close()

    programs = []
    for row in rows:
        programs.append({
            "program_id": row["program_id"],
            "name": row["name"],
            "category": row["category"],
            "provider": row["provider"],
            "eligibility": json.loads(row["eligibility_json"]),
            "official_url": row["official_url"],
            "document_checklist": json.loads(row["document_checklist"]),
            "apply_pathway": json.loads(row["apply_pathway"])
        })
    return programs

# ---------------------------------------------------------
# DETERMINISTIC MATCHING ENGINE WITH DISABILITY SUPPORT
# ---------------------------------------------------------
def evaluate_eligibility(user_profile: Dict[str, Any], program: Dict[str, Any]) -> Dict[str, Any]:
    rules = program["eligibility"]
    reasons = []
    missing_info = []

    is_disabled = user_profile.get("is_disabled", False)

    if program["category"] != user_profile.get("category"):
        return {"status": "Ineligible", "reasons": ["Program belongs to a different domain"], "missing_info": []}

    # Income Evaluation
    max_income = rules.get("max_income")
    user_income = user_profile.get("monthly_income")
    if max_income is not None and user_income is not None:
        if user_income > max_income:
            reasons.append(f"Monthly household income (PKR {user_income:,}) exceeds maximum limit of PKR {max_income:,}.")

    # Age Evaluation
    min_age = rules.get("min_age", 0)
    max_age = rules.get("max_age", 120)
    user_age = user_profile.get("age")
    if user_age is not None:
        if user_age < min_age or user_age > max_age:
            reasons.append(f"Age {user_age} is outside the allowed bracket of {min_age} to {max_age} years.")

    # Domicile / Region
    allowed_regions = rules.get("allowed_regions", [])
    user_region = user_profile.get("domicile")
    if allowed_regions and user_region:
        if "All" not in allowed_regions and user_region not in allowed_regions:
            reasons.append(f"Domicile/Location '{user_region}' is not eligible. Allowed regions: {', '.join(allowed_regions)}.")

    # Driving License Check
    requires_license = rules.get("requires_license", False)
    has_license = user_profile.get("has_driving_license", False)
    if requires_license and not has_license:
        missing_info.append("Valid Learner or Permanent Driving License required.")

    # Education Qualification
    min_edu = rules.get("min_education_level")
    user_edu = user_profile.get("education_level")
    edu_levels = ["Primary", "Matric", "Intermediate", "Bachelors", "Masters", "PhD"]
    if min_edu and user_edu:
        if user_edu in edu_levels and min_edu in edu_levels:
            if edu_levels.index(user_edu) < edu_levels.index(min_edu):
                reasons.append(f"Educational level '{user_edu}' is below required baseline of '{min_edu}'.")

    # Disability Quota Rules
    requires_disability = rules.get("disability_quota_only", False)
    if requires_disability and not is_disabled:
        reasons.append("Reserved exclusively for Persons with Disabilities (PWD) holding a NADRA Special CNIC / Certificate.")

    # Exemption for PWD candidates on laptop merit caps
    if is_disabled and program["program_id"] == "CM_PUNJAB_LAPTOP":
        reasons = [r for r in reasons if "Educational level" not in r]

    if reasons:
        return {"status": "Ineligible", "reasons": reasons, "missing_info": missing_info}
    elif missing_info:
        return {"status": "Conditional", "reasons": ["Meets income & age bounds, but missing mandatory documents or licenses."], "missing_info": missing_info}
    else:
        status_msg = ["All criteria satisfied."]
        if is_disabled:
            status_msg.append("Eligible under Special Persons / Disability Reserved Quotas.")
        return {"status": "Eligible", "reasons": status_msg, "missing_info": []}

def run_matching_pipeline(user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    all_programs = fetch_all_programs()
    results = []
    eligible_ids = []

    for prog in all_programs:
        if prog["category"] == user_profile.get("category"):
            eval_res = evaluate_eligibility(user_profile, prog)
            matched_record = {
                "program": prog,
                "status": eval_res["status"],
                "reasons": eval_res["reasons"],
                "missing_info": eval_res["missing_info"]
            }
            results.append(matched_record)
            if eval_res["status"] in ["Eligible", "Conditional"]:
                eligible_ids.append(prog["program_id"])

    save_search_history(
        user_id=user_profile.get("user_id"),
        category=user_profile.get("category", "General"),
        profile=user_profile,
        matches=eligible_ids
    )
    return results

# ---------------------------------------------------------
# GROQ BILINGUAL AI CHATBOT
# ---------------------------------------------------------
class GroqAssistant:
    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
        self.model_name = model_name

    def generate_bilingual_response(self, user_query: str, history: List[Dict[str, str]] = None) -> str:
        system_prompt = (
            "You are AidMatch AI (مددگار AI), an official assistant for Pakistani government welfare, "
            "scholarships, disability quotas, free IT training, and bike/laptop schemes.\n"
            "OPERATIONAL GUIDELINES:\n"
            "1. Respond seamlessly in English or Urdu (اردو) depending on user input.\n"
            "2. Highlight special disability quotas (2% reserved in HEC/Govt admissions & jobs) when asked.\n"
            "3. Official Links Reference:\n"
            "   - Scholarships & Welfare: https://bisp.gov.pk/, https://honhaarscholarship.punjabhec.gov.pk/, https://ehsaas.punjab.gov.pk/, https://pspa.punjab.gov.pk/what-we-do, https://scholarship.hec.gov.pk/, https://eservices.hec.gov.pk/, https://www.pass.gov.pk/, https://www.sef.org.pk/, https://pmyp.gov.pk/\n"
            "   - Free Courses: https://navttc.gov.pk/courses/, https://digiskills.pk/, https://dlsei.hec.gov.pk/, https://www.psdf.org.pk/, https://www.kpitb.gov.pk/, https://www.tevta.gop.pk/, http://www.stevta.gos.pk/, https://buildyourfuture.withgoogle.com/, https://www.netacad.com/catalogs/learn, https://www.pakangels.com/hec-generative-ai-training-program/\n"
            "   - Asset Schemes: https://bikes.punjab.gov.pk/, https://cmlaptophed.punjab.gov.pk/, https://pmyp.gov.pk/\n"
            "4. Provide clean, bulleted step-by-step guidance."
        )

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_query})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to AI service: {str(e)}"
