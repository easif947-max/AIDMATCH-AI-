import os
import json
import sqlite3
import backend

if os.path.exists("aidmatch.db"):
    os.remove("aidmatch.db")

backend.init_db()

SEED_PROGRAMS = [
    # ------------------ SCHOLARSHIPS & WELFARE ------------------
    {
        "program_id": "HONHAAR_PUNJAB",
        "name": "CM Punjab Honhaar Undergraduate Scholarship",
        "category": "💰 Scholarships & Financial Assistance",
        "provider": "Punjab Higher Education Commission (PHEC)",
        "eligibility_json": json.dumps({"max_income": 350000, "min_age": 16, "max_age": 30, "allowed_regions": ["Punjab"], "requires_license": False, "min_education_level": "Intermediate", "disability_quota_only": False}),
        "official_url": "https://honhaarscholarship.punjabhec.gov.pk/",
        "document_checklist": json.dumps(["Punjab Domicile", "Intermediate Marks Sheet (65%+ Arts / 70%+ Science)", "Family Income Affidavit (< PKR 350,000)", "CNIC / B-Form"]),
        "apply_pathway": json.dumps(["Register on honhaarscholarship.punjabhec.gov.pk", "Fill academic & household details", "Upload e-stamp income affidavit and submit"])
    },
    {
        "program_id": "BISP_OFFICIAL",
        "name": "Benazir Income Support Programme (BISP Official)",
        "category": "💰 Scholarships & Financial Assistance",
        "provider": "BISP Government of Pakistan",
        "eligibility_json": json.dumps({"max_income": 40000, "min_age": 18, "max_age": 80, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://bisp.gov.pk/",
        "document_checklist": json.dumps(["NADRA Biometric CNIC", "NSER Dynamic Survey Record"]),
        "apply_pathway": json.dumps(["Visit nearest BISP Dynamic Registration Center", "Complete NSER survey", "Receive payment notifications via 8171"])
    },
    {
        "program_id": "EHSAAS_PUNJAB",
        "name": "Ehsaas Rashan & Social Safety Punjab",
        "category": "💰 Scholarships & Financial Assistance",
        "provider": "Ehsaas Program Punjab",
        "eligibility_json": json.dumps({"max_income": 50000, "min_age": 18, "max_age": 75, "allowed_regions": ["Punjab"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://ehsaas.punjab.gov.pk/",
        "document_checklist": json.dumps(["CNIC Registered SIM", "Punjab Domicile / Address"]),
        "apply_pathway": json.dumps(["Register CNIC on ehsaas.punjab.gov.pk portal", "Get subsidy confirmation SMS for merchant stores"])
    },
    {
        "program_id": "PSPA_PROGRAMS",
        "name": "PSPA Welfare Schemes (Humqadam, Ba-Himmat & Masawaat)",
        "category": "💰 Scholarships & Financial Assistance",
        "provider": "Punjab Social Protection Authority (PSPA)",
        "eligibility_json": json.dumps({"max_income": 45000, "min_age": 18, "max_age": 80, "allowed_regions": ["Punjab"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://pspa.punjab.gov.pk/what-we-do",
        "document_checklist": json.dumps(["NADRA Special CNIC with Disability Logo (for Humqadam)", "Senior Citizen CNIC 65+ (for Ba-Himmat)", "Transgender CNIC (for Masawaat)"]),
        "apply_pathway": json.dumps(["Review program details on pspa.punjab.gov.pk/what-we-do", "Register at nearest PSPA/DHQ center with NADRA disability card"])
    },
    {
        "program_id": "HEC_NEED_BASED",
        "name": "HEC Need-Based Undergraduate Scholarship",
        "category": "💰 Scholarships & Financial Assistance",
        "provider": "Higher Education Commission (HEC)",
        "eligibility_json": json.dumps({"max_income": 60000, "min_age": 17, "max_age": 30, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Intermediate", "disability_quota_only": False}),
        "official_url": "https://scholarship.hec.gov.pk/",
        "document_checklist": json.dumps(["CNIC of Self & Father", "Monthly Utility Bills", "Father/Guardian Income Certificate", "Disability Certificate (if claiming PWD quota)"]),
        "apply_pathway": json.dumps(["Create profile on scholarship.hec.gov.pk", "Submit online form and select institution", "Provide financial records to university FAO office"])
    },
    {
        "program_id": "HEC_ESERVICES_PORTAL",
        "name": "HEC National & Overseas Merit Scholarships",
        "category": "💰 Scholarships & Financial Assistance",
        "provider": "HEC E-Services Portal",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 18, "max_age": 35, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Bachelors", "disability_quota_only": False}),
        "official_url": "https://eservices.hec.gov.pk/",
        "document_checklist": json.dumps(["Attested Degrees & Transcripts", "HAT/GRE Test Scorecard", "NADRA Special CNIC (for reserved seats)"]),
        "apply_pathway": json.dumps(["Register at eservices.hec.gov.pk", "Select active national/international calls", "Upload academic & disability documents"])
    },
    {
        "program_id": "SEF_SCHOLARSHIPS",
        "name": "Sindh Education Foundation (SEF) Student Grants",
        "category": "💰 Scholarships & Financial Assistance",
        "provider": "Sindh Education Foundation",
        "eligibility_json": json.dumps({"max_income": 45000, "min_age": 10, "max_age": 22, "allowed_regions": ["Sindh"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://www.sef.org.pk/",
        "document_checklist": json.dumps(["B-Form / CNIC", "Sindh Domicile", "School Enrollment Certificate"]),
        "apply_pathway": json.dumps(["Apply directly via SEF partner schools", "Submit domicile & family financial records"])
    },
    {
        "program_id": "PMYP_SCHOLARSHIP",
        "name": "Prime Minister's Youth Financial Support Scheme",
        "category": "💰 Scholarships & Financial Assistance",
        "provider": "Prime Minister Youth Programme (PMYP)",
        "eligibility_json": json.dumps({"max_income": 80000, "min_age": 15, "max_age": 29, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Intermediate", "disability_quota_only": False}),
        "official_url": "https://pmyp.gov.pk/",
        "document_checklist": json.dumps(["CNIC / B-Form", "Student Card", "Income proof of parents"]),
        "apply_pathway": json.dumps(["Apply online via pmyp.gov.pk", "Track application status through PM portal"])
    },

    # ------------------ COURSES ------------------
    {
        "program_id": "NAVTTC_COURSES",
        "name": "NAVTTC Prime Minister's High-Tech Skill Training",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "National Vocational and Technical Training Commission",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 18, "max_age": 40, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Matric", "disability_quota_only": False}),
        "official_url": "https://navttc.gov.pk/courses/",
        "document_checklist": json.dumps(["CNIC Copy", "Educational Certificates", "2 Passport Photos"]),
        "apply_pathway": json.dumps(["Browse courses at navttc.gov.pk/courses/", "Apply online or visit nearest institute", "Appear for interview/selection"])
    },
    {
        "program_id": "DIGISKILLS_FREE",
        "name": "DigiSkills 2.0 Freelancing & Digital Training",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "IGNITE / Ministry of IT & Telecom",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 12, "max_age": 70, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://digiskills.pk/",
        "document_checklist": json.dumps(["CNIC / B-Form", "Active Email Address"]),
        "apply_pathway": json.dumps(["Create account at digiskills.pk", "Enroll in 2 courses during open batch registration", "Watch online video lectures"])
    },
    {
        "program_id": "HEC_DLSEI",
        "name": "HEC Digital Learning & Skills Initiative (Coursera)",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "HEC & Coursera",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 17, "max_age": 35, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Intermediate", "disability_quota_only": False}),
        "official_url": "https://dlsei.hec.gov.pk/",
        "document_checklist": json.dumps(["Student/Faculty University ID", "CNIC"]),
        "apply_pathway": json.dumps(["Register at dlsei.hec.gov.pk", "Get verification from university focal person", "Access Coursera catalog"])
    },
    {
        "program_id": "PSDF_SKILLS",
        "name": "PSDF Free Vocational & Technical Training",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "Punjab Skills Development Fund",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 15, "max_age": 35, "allowed_regions": ["Punjab"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://www.psdf.org.pk/",
        "document_checklist": json.dumps(["Punjab Domicile", "CNIC / B-Form"]),
        "apply_pathway": json.dumps(["Search courses on psdf.org.pk", "Enroll in nearest PSDF affiliated institute"])
    },
    {
        "program_id": "KPITB_SKILLS",
        "name": "KPITB Digital Youth Empowerment Courses",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "Khyber Pakhtunkhwa IT Board",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 16, "max_age": 35, "allowed_regions": ["KPK"], "requires_license": False, "min_education_level": "Matric", "disability_quota_only": False}),
        "official_url": "https://www.kpitb.gov.pk/",
        "document_checklist": json.dumps(["KPK Domicile", "CNIC"]),
        "apply_pathway": json.dumps(["Visit kpitb.gov.pk", "Apply for active digital training bootcamps"])
    },
    {
        "program_id": "TEVTA_PUNJAB",
        "name": "TEVTA Short Technical & Vocational Courses",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "TEVTA Punjab",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 14, "max_age": 40, "allowed_regions": ["Punjab"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://www.tevta.gop.pk/",
        "document_checklist": json.dumps(["Punjab Domicile", "Educational Marks Sheet"]),
        "apply_pathway": json.dumps(["Choose course on tevta.gop.pk", "Submit physical form at local TEVTA center"])
    },
    {
        "program_id": "STEVTA_SINDH",
        "name": "STEVTA Technical & Vocational Training Programs",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "Sindh TEVTA",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 14, "max_age": 40, "allowed_regions": ["Sindh"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "http://www.stevta.gos.pk/",
        "document_checklist": json.dumps(["Sindh Domicile", "CNIC / B-Form"]),
        "apply_pathway": json.dumps(["Apply online at stevta.gos.pk or regional institute"])
    },
    {
        "program_id": "GOOGLE_BUILD_FUTURE",
        "name": "Google Career Certificates & Student Developer Training",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "Google / Tech4Good",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 15, "max_age": 60, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://buildyourfuture.withgoogle.com/",
        "document_checklist": json.dumps(["Active Google Account"]),
        "apply_pathway": json.dumps(["Explore programs at buildyourfuture.withgoogle.com", "Join self-paced online learning pathways"])
    },
    {
        "program_id": "CISCO_NETACAD",
        "name": "Cisco Networking Academy Free IT & Cybersecurity Courses",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "Cisco Systems",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 13, "max_age": 70, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Primary", "disability_quota_only": False}),
        "official_url": "https://www.netacad.com/catalogs/learn",
        "document_checklist": json.dumps(["Valid Email Address"]),
        "apply_pathway": json.dumps(["Enroll directly at netacad.com", "Complete free courses on Linux, Cybersecurity, and Networking"])
    },
    {
        "program_id": "HEC_GENAI_PAKANGELS",
        "name": "HEC Generative AI National Training Program",
        "category": "🎓 Free Courses & Skill Development",
        "provider": "HEC & PakAngels",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 18, "max_age": 45, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Intermediate", "disability_quota_only": False}),
        "official_url": "https://www.pakangels.com/hec-generative-ai-training-program/",
        "document_checklist": json.dumps(["CNIC", "Basic Programming Knowledge"]),
        "apply_pathway": json.dumps(["Register via pakangels.com page", "Complete AI assessment & join live cohort"])
    },

    # ------------------ ASSET SCHEMES ------------------
    {
        "program_id": "CM_PUNJAB_EBIKE",
        "name": "CM Punjab E-Bike & Scooty Scheme",
        "category": "🛵 Govt Asset Schemes (Bikes & Laptops)",
        "provider": "PITB & Transport Department Punjab",
        "eligibility_json": json.dumps({"max_income": 150000, "min_age": 18, "max_age": 35, "allowed_regions": ["Punjab"], "requires_license": True, "min_education_level": "Matric", "disability_quota_only": False}),
        "official_url": "https://bikes.punjab.gov.pk/",
        "document_checklist": json.dumps(["CNIC", "Punjab Domicile", "Driving/Learner License", "Special Person CNIC (for PWD reserved quota)"]),
        "apply_pathway": json.dumps(["Register on bikes.punjab.gov.pk", "Select E-bike or Scooty model", "Upload license and bank verification documents"])
    },
    {
        "program_id": "CM_PUNJAB_LAPTOP",
        "name": "CM Punjab Free Laptop Scheme",
        "category": "🛵 Govt Asset Schemes (Bikes & Laptops)",
        "provider": "Higher Education Department (HED) Punjab",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 16, "max_age": 30, "allowed_regions": ["Punjab"], "requires_license": False, "min_education_level": "Intermediate", "disability_quota_only": False}),
        "official_url": "https://cmlaptophed.punjab.gov.pk/",
        "document_checklist": json.dumps(["CNIC / B-Form", "Punjab Domicile", "Transcript (65%+ required; Blind/Disabled candidates exempt)", "NADRA Disability Certificate"]),
        "apply_pathway": json.dumps(["Verify CNIC at cmlaptophed.punjab.gov.pk", "Confirm university roll number & merit standing", "Receive laptop from campus distribution center"])
    },
    {
        "program_id": "PMYP_ASSET_LAPTOP",
        "name": "Prime Minister's Youth Laptop & Business Loan Schemes",
        "category": "🛵 Govt Asset Schemes (Bikes & Laptops)",
        "provider": "PM Youth Programme",
        "eligibility_json": json.dumps({"max_income": None, "min_age": 18, "max_age": 35, "allowed_regions": ["All"], "requires_license": False, "min_education_level": "Intermediate", "disability_quota_only": False}),
        "official_url": "https://pmyp.gov.pk/",
        "document_checklist": json.dumps(["CNIC", "University Student ID", "Disability Card (for reserved allocation)"]),
        "apply_pathway": json.dumps(["Apply online via pmyp.gov.pk", "Select laptop or asset loan portal", "Track application online"])
    }
]

conn = backend.get_db_connection()
cursor = conn.cursor()
for prog in SEED_PROGRAMS:
    cursor.execute("""
        INSERT OR REPLACE INTO programs (program_id, name, category, provider, eligibility_json, official_url, document_checklist, apply_pathway)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (prog["program_id"], prog["name"], prog["category"], prog["provider"], prog["eligibility_json"], prog["official_url"], prog["document_checklist"], prog["apply_pathway"]))

conn.commit()
conn.close()

print("✅ Comprehensive dataset seeded into aidmatch.db with all official links.")
