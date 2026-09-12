import streamlit as st
import json
from backend import init_db, register_user, authenticate_user, run_matching_pipeline, get_user_search_history, GroqAssistant

st.set_page_config(page_title="AidMatch Pakistan", page_icon="🇵🇰", layout="wide")

# High-Contrast Dark Theme CSS
st.markdown("""
<style>
    .main-header { font-size: 2.4rem; color: #10b981; font-weight: 800; text-align: center; margin-bottom: 5px; }
    .sub-header { font-size: 1.1rem; color: #9ca3af; text-align: center; margin-bottom: 25px; }

    /* Modern Header Banner Cards */
    .program-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border-radius: 12px;
        padding: 22px 25px;
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        border: 1px solid #374151;
    }
    .card-eligible { border-left: 8px solid #10b981; }
    .card-conditional { border-left: 8px solid #f59e0b; }
    .card-ineligible { border-left: 8px solid #ef4444; }

    .program-title {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0 0 8px 0 !important;
        line-height: 1.3 !important;
        letter-spacing: -0.01em !important;
    }
    .program-provider {
        font-size: 1.05rem !important;
        color: #38bdf8 !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    .badge-eligible {
        background-color: #10b981;
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-conditional {
        background-color: #f59e0b;
        color: #000000;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-ineligible {
        background-color: #ef4444;
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

init_db()

# Automatically run seeding script if database programs table is empty
import seed

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# AUTHENTICATION WALL
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🇵🇰 AidMatch Pakistan</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Free Government Schemes, Scholarships & Skill Discovery Portal</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔒 Sign In", "📝 Create Account"])

        with tab1:
            st.subheader("Sign In to Your Private Account")
            login_email = st.text_input("Gmail / Email Address", key="login_email")
            login_pass = st.text_input("Password", type="password", key="login_pass")

            if st.button("Sign In", use_container_width=True):
                if login_email and login_pass:
                    res = authenticate_user(login_email, login_pass)
                    if res["success"]:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = res["user"]
                        st.success("Authenticated successfully!")
                        st.rerun()
                    else:
                        st.error(res["error"])
                else:
                    st.warning("Please enter both email and password.")

        with tab2:
            st.subheader("Create New Private Account")
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Gmail / Email Address", key="reg_email")
            reg_cnic = st.text_input("13-Digit CNIC", key="reg_cnic")
            reg_pass = st.text_input("Set Private Password", type="password", key="reg_pass")

            if st.button("Create Account & Sign In", use_container_width=True):
                if reg_name and reg_email and reg_cnic and reg_pass:
                    res = register_user(reg_email, reg_pass, reg_cnic, reg_name)
                    if res["success"]:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = res["user"]
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(res["error"])
                else:
                    st.warning("All fields are required.")
    st.stop()

# PRIVATE LOGGED-IN SIDEBAR
st.sidebar.title(f"👤 {st.session_state['user']['name']}")
st.sidebar.caption(f"Logged in as: {st.session_state['user']['email']}")

nav_choice = st.sidebar.radio("Navigation Category", [
    "🎓 Free Courses & Skill Development",
    "💰 Scholarships & Financial Assistance",
    "🛵 Govt Asset Schemes (Bikes & Laptops)",
    "📜 Private Search History",
    "💬 Bilingual Assistant / مددگار"
])

if st.sidebar.button("Logout / Lock Session"):
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["messages"] = []
    st.rerun()

# RESULTS RENDERER
def render_all_results(results):
    st.subheader(f"📊 Evaluated Opportunities Matrix ({len(results)} Total Programs)")
    st.caption("All programs in this category are evaluated for your account profile.")

    if not results:
        st.info("No records found.")
        return

    sorted_results = sorted(results, key=lambda x: 0 if x["status"] == "Eligible" else 1 if x["status"] == "Conditional" else 2)

    for res in sorted_results:
        prog = res["program"]
        status = res["status"]
        card_class = f"card-{status.lower()}"
        badge_class = f"badge-{status.lower()}"

        st.markdown(f"""
        <div class='program-card {card_class}'>
            <div style='display: flex; justify-content: space-between; align-items: flex-start; gap: 15px;'>
                <div style='flex-grow: 1;'>
                    <div class='program-title'>🏛️ {prog['name']}</div>
                    <div class='program-provider'><b>Managing Provider:</b> {prog['provider']}</div>
                </div>
                <div>
                    <span class='{badge_class}'>{status}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if status == "Ineligible":
            st.error("**❌ Why You Are Not Eligible:**")
            for r in res["reasons"]:
                st.write(f"• {r}")
        elif status == "Conditional":
            st.warning("**⚠️ Conditional Eligibility Notes:**")
            for r in res["reasons"]:
                st.write(f"• {r}")
            if res["missing_info"]:
                st.write("**Action Needed:** " + ", ".join(res["missing_info"]))
        else:
            st.success("**✅ You Meet All Eligibility Criteria!**")
            for r in res["reasons"]:
                st.write(f"• {r}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**📋 Required Documents & Quotas:**")
            for doc in prog["document_checklist"]:
                st.checkbox(doc, key=f"{prog['program_id']}_{doc}")
        with col_b:
            st.write("**🚀 Direct Application Pathway:**")
            for idx, step in enumerate(prog["apply_pathway"], 1):
                st.write(f"{idx}. {step}")

        st.link_button(f"Visit Official Portal ({prog['provider']})", prog["official_url"])
        st.divider()

# CATEGORY EVALUATION FORMS
if nav_choice in ["🎓 Free Courses & Skill Development", "💰 Scholarships & Financial Assistance", "🛵 Govt Asset Schemes (Bikes & Laptops)"]:
    st.title(nav_choice)

    with st.form("search_form"):
        st.subheader("📋 Profile Evaluation Form")
        col1, col2 = st.columns(2)
        with col1:
            income = st.number_input("Monthly Household Income (PKR)", min_value=0, value=45000, step=5000)
            age = st.number_input("Applicant Age", min_value=10, max_value=80, value=22)
            domicile = st.selectbox("Domicile / Residence District", ["Punjab", "Federal / ICT", "Sindh", "KPK", "Balochistan", "AJK / GB"])
        with col2:
            education = st.selectbox("Current / Highest Qualification", ["Primary", "Matric", "Intermediate", "Bachelors", "Masters", "PhD"])
            is_disabled = st.checkbox("♿ Person with Disability / Special Person (Holding NADRA Special CNIC / Certificate)")
            license_status = st.checkbox("🛵 Holds Valid Driving / Learner License") if "Asset Schemes" in nav_choice else False

        submit_btn = st.form_submit_button("Evaluate All Programs in This Category")

    if submit_btn:
        profile = {
            "user_id": st.session_state["user"]["user_id"],
            "cnic": st.session_state["user"]["cnic"],
            "category": nav_choice,
            "monthly_income": income,
            "age": age,
            "domicile": domicile,
            "education_level": education,
            "is_disabled": is_disabled,
            "has_driving_license": license_status
        }
        results = run_matching_pipeline(profile)
        render_all_results(results)

# PRIVATE SEARCH HISTORY LOG
elif nav_choice == "📜 Private Search History":
    st.title("📜 Private Search History Log")
    st.caption("This log contains only search queries performed under your account.")

    history = get_user_search_history(st.session_state["user"]["user_id"])

    if not history:
        st.info("No saved search history found for your account.")
    else:
        for item in history:
            with st.expander(f"Search Record #{item['search_id']} - {item['category']} ({item['timestamp']})"):
                st.json(item["profile"])
                st.write(f"Matched Program IDs: `{item['matches']}`")

# BILINGUAL CHATBOT
elif nav_choice == "💬 Bilingual Assistant / مددگار":
    st.title("💬 Bilingual Assistant / مددگار AI")
    st.caption("Ask questions about disability quotas, document requirements, or portal applications in English or Urdu.")

    bot = GroqAssistant()

    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("سوال پوچھیں یا کہئے Ask a question...")
    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching official guidance..."):
                response = bot.generate_bilingual_response(user_input, st.session_state["messages"][:-1])
                st.write(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})
