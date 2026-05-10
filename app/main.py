from pathlib import Path
from io import BytesIO

import pandas as pd
import streamlit as st
import plotly.express as px

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from agent import process_invoice_rules, generate_email_for_invoice, approve_and_send


PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGIN_IMAGE = PROJECT_ROOT / "assets" / ",..jpeg"
FALLBACK_IMAGE = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"


def get_image_path():
    if LOGIN_IMAGE.exists():
        return str(LOGIN_IMAGE)
    return FALLBACK_IMAGE


def get_recovery_probability(risk):
    if risk == "LOW":
        return 90
    elif risk == "MEDIUM":
        return 65
    else:
        return 30


def generate_pdf_report(logs_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("CollectAI Finance Audit Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    for _, row in logs_df.iterrows():
        text = f"""
        Invoice: {row['invoice_no']}<br/>
        Client: {row['client_name']}<br/>
        Stage: {row['stage']}<br/>
        Tone: {row['tone']}<br/>
        Risk: {row['risk']}<br/>
        Status: {row['status']}<br/>
        """
        elements.append(Paragraph(text, styles["BodyText"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


st.set_page_config(
    page_title="CollectAI Finance Agent",
    page_icon="💼",
    layout="wide"
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:

    st.image(
        get_image_path(),
        use_container_width=True
    )

    st.markdown(
        """
        <div style='text-align:center; margin-top:20px; margin-bottom:25px;'>
            <h2 style='color:#0077A3;'>🔐 Secure Login</h2>
            <p style='color:#6B7280;'>Access CollectAI Finance Recovery System</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("🔐 Login", use_container_width=True):
        if username == "admin" and password == "admin123":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()


if "request_count" not in st.session_state:
    st.session_state["request_count"] = 0

st.session_state["request_count"] += 1

if st.session_state["request_count"] > 50:
    st.error("Rate limit exceeded.")
    st.stop()


st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #0F4C5C 0%,
        #146C78 35%,
        #1B7F8A 70%,
        #2C9DA8 100%
    );
    color: white;
}

h1, h2, h3 {
    color: white;
    font-weight: 700;
}

[data-testid="stMetric"] {
    background: rgba(15, 118, 110, 0.92);
    backdrop-filter: blur(10px);
    padding: 18px;
    border-radius: 16px;
    color: white;
    box-shadow: 0px 8px 24px rgba(15, 118, 110, 0.22);
    border: 1px solid rgba(255,255,255,0.25);
}

div[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #CBD5E1;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #ECFDF5 0%,
        #E0F2FE 100%
    );
    border-right: 1px solid #CBD5E1;
}

section[data-testid="stSidebar"] * {
    color: #0F172A;
}

.stButton>button {
    background-color: #0F766E;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #115E59;
    color: white;
}

.stTextInput input,
.stTextArea textarea {
    background-color: rgba(255,255,255,0.92);
    color: #0F172A;
    border-radius: 10px;
    border: 1px solid #CBD5E1;
}

div[data-baseweb="notification"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


st.title("💼 CollectAI — Finance Credit Follow-Up Agent")

st.caption(
    "AI-powered overdue invoice follow-up with tone escalation, "
    "risk scoring, dry-run email sending, and audit logging."
)

st.sidebar.image(
    FALLBACK_IMAGE,
    width=90
)

st.sidebar.title("CollectAI Console")

st.sidebar.image(
    get_image_path(),
    use_container_width=True
)

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

uploaded_file = st.sidebar.file_uploader(
    "Upload Invoice CSV",
    type=["csv"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Project Status")
st.sidebar.success("AI Agent Active")
st.sidebar.info("Mode: Dry-Run / Sandbox")

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Tech Stack")
st.sidebar.write("LLM: Gemini 2.0 Flash")
st.sidebar.write("Framework: LangChain")
st.sidebar.write("UI: Streamlit")
st.sidebar.write("Logging: JSON Audit Log")

st.sidebar.markdown("---")
st.sidebar.subheader("🔐 Safety")
st.sidebar.write("✅ No real emails sent")
st.sidebar.write("✅ Human approval required")
st.sidebar.write("✅ Emails masked")
st.sidebar.write("✅ API key in .env")


if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("../data/invoices.csv")
    df.columns = df.columns.str.strip().str.lower()

required_columns = [
    "invoice_no",
    "client_name",
    "amount",
    "due_date",
    "contact_email",
    "followup_count"
]

missing_cols = [
    col for col in required_columns
    if col not in df.columns
]

if missing_cols:
    st.error(
        f"CSV missing required columns: {', '.join(missing_cols)}"
    )
    st.info(f"Detected Columns: {list(df.columns)}")
    st.stop()

required_columns = [
    "invoice_no",
    "client_name",
    "amount",
    "due_date",
    "contact_email",
    "followup_count"
]

missing_cols = [
    col for col in required_columns
    if col not in df.columns
]

if missing_cols:
    st.error(
        f"CSV missing required columns: {', '.join(missing_cols)}"
    )
    st.stop()

df["due_date"] = pd.to_datetime(df["due_date"]).dt.date
results = []

for _, row in df.iterrows():
    result = process_invoice_rules(row)
    results.append(result)

processed = [r["invoice"] for r in results]
processed_df = pd.DataFrame(processed)

processed_df["recovery_probability"] = processed_df["risk"].apply(
    get_recovery_probability
)


st.subheader("🏆 Executive Summary")

total_outstanding = processed_df["amount"].sum()
high_risk_cases = len(processed_df[processed_df["risk"] == "HIGH"])
potential_escalations = len(
    processed_df[processed_df["stage"] == "Escalation Flag"]
)

if high_risk_cases > 0:
    priority = "High Priority Recovery Required"
elif potential_escalations > 0:
    priority = "Escalation Monitoring Required"
else:
    priority = "Normal Recovery Flow"

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

summary_col1.metric("Total Outstanding", f"₹{total_outstanding:,.0f}")
summary_col2.metric("High Risk Cases", high_risk_cases)
summary_col3.metric("Potential Escalations", potential_escalations)
summary_col4.metric("Recovery Priority", priority)


st.subheader("📊 Finance Recovery Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Invoices", len(processed_df))
col2.metric("Overdue Invoices", len(processed_df[processed_df["days_overdue"] > 0]))
col3.metric("High Risk Cases", len(processed_df[processed_df["risk"] == "HIGH"]))
col4.metric("Escalated Cases", len(processed_df[processed_df["stage"] == "Escalation Flag"]))


chart1, chart2 = st.columns(2)

with chart1:
    risk_count = processed_df["risk"].value_counts().reset_index()
    risk_count.columns = ["Risk", "Count"]

    fig = px.pie(
        risk_count,
        names="Risk",
        values="Count",
        title="Risk Distribution",
        hole=0.45,
        color_discrete_sequence=[
            "#14B8A6",
            "#0EA5E9",
            "#EF4444"
        ]
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        paper_bgcolor="#F4F7FA",
        plot_bgcolor="#F4F7FA",
        font=dict(color="#0F172A", size=14)
    )

    st.plotly_chart(fig, use_container_width=True)

with chart2:
    stage_count = processed_df["stage"].value_counts().reset_index()
    stage_count.columns = ["Stage", "Count"]

    fig = px.pie(
        stage_count,
        names="Stage",
        values="Count",
        title="Escalation Stage Distribution",
        hole=0.45,
        color_discrete_sequence=[
            "#14B8A6",
            "#0EA5E9",
            "#F97316",
            "#EF4444",
            "#8B5CF6"
        ]
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig.update_layout(
        paper_bgcolor="#F4F7FA",
        plot_bgcolor="#F4F7FA",
        font=dict(color="#0F172A", size=14)
    )

    st.plotly_chart(fig, use_container_width=True)


st.subheader("🧠 AI Recovery Insights")

highest_risk = processed_df.sort_values(
    by=["days_overdue", "amount"],
    ascending=False
).iloc[0]

st.markdown(
    f"""
    <div style="color:white; font-size:18px; line-height:1.8;">

    Most critical recovery case is
    <b>{highest_risk['client_name']}</b>.

    <br><br>

    Invoice <b>{highest_risk['invoice_no']}</b>
    is overdue by <b>{highest_risk['days_overdue']} days</b>
    with an outstanding amount of
    <b>₹{highest_risk['amount']}</b>.

    <br><br>

    Recommended Action:
    <b>Immediate finance follow-up or escalation review.</b>

    </div>
    """,
    unsafe_allow_html=True
)


st.subheader("📌 Invoice Queue")

st.dataframe(
    processed_df[
        [
            "invoice_no",
            "client_name",
            "amount",
            "due_date",
            "masked_email",
            "days_overdue",
            "followup_count",
            "stage",
            "tone",
            "risk",
            "recovery_probability"
        ]
    ],
    use_container_width=True
)


st.subheader("🤖 AI Follow-Up Workspace")

invoice_numbers = processed_df["invoice_no"].tolist()

selected_invoice_no = st.selectbox(
    "Select Invoice",
    invoice_numbers
)

selected_result = None

for result in results:
    if result["invoice"]["invoice_no"] == selected_invoice_no:
        selected_result = result
        break

invoice = selected_result["invoice"]

if "generated_email" not in st.session_state:
    st.session_state["generated_email"] = None

if "selected_invoice_no" not in st.session_state:
    st.session_state["selected_invoice_no"] = selected_invoice_no

if st.session_state["selected_invoice_no"] != selected_invoice_no:
    st.session_state["generated_email"] = None
    st.session_state["selected_invoice_no"] = selected_invoice_no

left, right = st.columns(2)

with left:
    st.markdown("### Invoice Details")

    st.write(f"**Client:** {invoice['client_name']}")
    st.write(f"**Invoice:** {invoice['invoice_no']}")
    st.write(f"**Amount:** ₹{invoice['amount']}")
    st.write(f"**Due Date:** {invoice['due_date']}")
    st.write(f"**Days Overdue:** {invoice['days_overdue']}")
    st.write(f"**Follow-up Count:** {invoice['followup_count']}")
    st.write(f"**Stage:** {invoice['stage']}")
    st.write(f"**Tone:** {invoice['tone']}")
    st.write(f"**Risk:** {invoice['risk']}")

    probability = get_recovery_probability(invoice["risk"])
    st.write(f"**Recovery Probability:** {probability}%")
    st.progress(probability / 100)

    confidence_score = max(60, 95 - invoice["days_overdue"])
    st.write(f"**AI Confidence Score:** {confidence_score}%")
    st.progress(confidence_score / 100)

    st.markdown(
    f"""
    <span style='color:white; font-size:18px; font-weight:600;'>
    Auto Trigger: {invoice['should_send']}
    </span>
    """,
    unsafe_allow_html=True
)

    if invoice["stage"] == "Escalation Flag":
        st.error("⚠ Escalated to Legal / Finance Review")

    st.markdown(
    f"""
    <div style="
        background-color:rgba(255,255,255,0.10);
        color:white;
        padding:16px;
        border-radius:12px;
        font-size:16px;
        font-weight:500;
    ">

    AI selected tone <b>{invoice['tone']}</b>
    because invoice is
    <b>{invoice['days_overdue']} days overdue</b>
    and
    <b>{invoice['followup_count']} reminder(s)</b>
    were already sent.

    </div>
    """,
    unsafe_allow_html=True
)

with right:
    st.markdown("### ✉️ AI Generated Email")

    if st.button("Generate AI Email"):
        st.session_state["generated_email"] = generate_email_for_invoice(invoice)

    email = st.session_state["generated_email"]

    if email is None:
        st.info("Click **Generate AI Email** to create the draft.")

    else:
        st.text_input(
            "Subject",
            value=email["subject"]
        )

        st.text_area(
            "Email Body",
            value=email["body"],
            height=300
        )

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("Approve Dry-Run Send"):
                send_result = approve_and_send(invoice, email)
                st.markdown("""
<style>

div[data-baseweb="notification"] {
    color: white !important;
    font-weight: 600;
    font-size: 16px;
}

</style>
""", unsafe_allow_html=True)

                st.markdown(
    f"""
    <div style="
        background-color:#14532D;
        color:white;
        padding:18px;
        border-radius:12px;
        font-weight:600;
        font-size:16px;
    ">

    Provider: {send_result['provider']}<br><br>

    Status: {send_result['status']}<br><br>

    Message: {send_result['message']}

    </div>
    """,
    unsafe_allow_html=True
)

        with col_b:
            if st.button("Reject Draft"):
                st.markdown("""
<div style="
background-color:#92400E;
color:white;
padding:15px;
border-radius:12px;
font-weight:600;
">
Draft rejected by human reviewer.
</div>
""", unsafe_allow_html=True)

        with col_c:
            if st.button("Escalate Manually"):
                st.markdown("""
<div style="
background-color:#7F1D1D;
color:white;
padding:15px;
border-radius:12px;
font-weight:600;
">
Invoice manually escalated to finance/legal review.
</div>
""", unsafe_allow_html=True)

        if st.button("Generate AI Call Script"):

            call_script = f"""
Hello {invoice['client_name']},

This is a follow-up from the Finance Team regarding Invoice #{invoice['invoice_no']} for ₹{invoice['amount']}.

The invoice was due on {invoice['due_date']} and is currently {invoice['days_overdue']} days overdue.

We noticed that {invoice['followup_count']} reminder(s) have already been sent.

Could you please confirm the expected payment date or complete the payment using this link:
{invoice['payment_link']}

Thank you.
"""

            st.text_area(
                "AI Collection Call Script",
                value=call_script,
                height=220
            )


st.subheader("🧾 Audit Logs")

st.caption(
    "Audit trail records every approved dry-run email with timestamp, invoice details, tone, risk, and send status."
)

try:
    logs_df = pd.read_json("../logs/audit_log.json")

    st.dataframe(
        logs_df,
        use_container_width=True
    )

    st.download_button(
        label="⬇️ Download CSV Audit Report",
        data=logs_df.to_csv(index=False),
        file_name="audit_report.csv",
        mime="text/csv"
    )

    pdf_data = generate_pdf_report(logs_df)

    st.markdown("""
<style>
div.stDownloadButton > button:first-child {
    background-color: white;
    color: black !important;
    font-weight: 700;
    border-radius: 10px;
    border: none;
    padding: 10px 18px;
}
</style>
""", unsafe_allow_html=True)

    st.download_button(
    label="📄 Download PDF Report",
    data=pdf_data,
    file_name="audit_report.pdf",
    mime="application/pdf"
)

except Exception:
    st.info(
        "No audit logs yet. "
        "Approve one dry-run email to create logs."
    )

st.markdown("---")

st.caption(
    "Built with Gemini AI • LangChain • Streamlit • Enterprise Recovery Workflow"
)