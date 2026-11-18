import os
import streamlit as st
from dotenv import load_dotenv

from pdf_utils import extract_pdf_text, create_question_pdf
from generator import analyze_syllabus, generate_questions, validate_questions

# =========================================================
# PAGE + CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Indala | AI Assessment Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_dotenv()

BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
QUESTION_TYPES = ["MCQ", "Short Answer", "Long Answer", "Case Study"]
DEFAULTS = {
    "syllabus_text": "",
    "analysis": None,
    "questions": [],
    "paper_settings": {},
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# NEW UI SYSTEM — GRAPHITE / IVORY / ELECTRIC LIME
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');

:root {
  --ink:#17211f; --muted:#687570; --paper:#f5f6f1; --white:#ffffff;
  --line:#e2e7df; --green:#b9ef58; --green-dark:#243b22;
  --panel:#202b28; --panel-2:#293632; --soft:#edf4e5;
}
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:var(--paper); color:var(--ink);}
.block-container {max-width:1480px;padding:2rem 3rem 3rem;}
h1,h2,h3,h4 {font-family:'Manrope',sans-serif!important;color:var(--ink);}
p, label, .stMarkdown {color:var(--ink);}
[data-testid="stSidebar"] {background:var(--panel);border-right:0;}
[data-testid="stSidebar"] * {color:#f5f8f3;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#c6d1ca;}
[data-testid="stSidebar"] hr {border-color:#43514b;}
[data-testid="stSidebar"] .stRadio label {padding:9px 12px;border-radius:10px;}
[data-testid="stSidebar"] .stRadio label:hover {background:#34443d;}
[data-testid="stSidebar"] [data-testid="stAlert"] {background:#2d3d36;border:1px solid #506057;}
[data-testid="stSidebar"] [data-testid="stAlert"] * {color:#f4f8f2!important;}

.hero {
  background:var(--panel); color:white; border-radius:24px; padding:30px 34px;
  position:relative; overflow:hidden; margin-bottom:22px;
  box-shadow:0 14px 36px rgba(24,39,33,.10);
}
.hero:after {content:"";position:absolute;width:250px;height:250px;border-radius:50%;
  background:rgba(185,239,88,.12);right:-55px;top:-115px;}
.hero-kicker {color:var(--green);font-size:.72rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;}
.hero h1 {color:#fff!important;font-size:clamp(1.8rem,3vw,2.65rem);font-weight:800;margin:10px 0 8px;}
.hero p {color:#c9d4ce!important;max-width:760px;margin:0;line-height:1.6;}
.hero-chip {display:inline-block;margin-top:19px;background:rgba(185,239,88,.13);
  color:var(--green);border:1px solid rgba(185,239,88,.25);padding:7px 12px;border-radius:30px;
  font-size:.78rem;font-weight:700;}
.eyebrow {color:#718078;font-size:.72rem;font-weight:800;letter-spacing:1.6px;text-transform:uppercase;}
.page-title {font-family:'Manrope',sans-serif;font-size:1.65rem;font-weight:800;margin:3px 0 4px;color:var(--ink);}
.page-subtitle {color:var(--muted);font-size:.92rem;margin-bottom:18px;}
.panel {
  background:#fff;border:1px solid var(--line);border-radius:18px;padding:22px 24px;
  box-shadow:0 5px 20px rgba(30,47,39,.035);margin-bottom:16px;
}
.mini-card {background:#fff;border:1px solid var(--line);border-radius:15px;padding:16px 18px;}
.mini-label {font-size:.73rem;color:#718078;font-weight:700;text-transform:uppercase;letter-spacing:.8px;}
.mini-value {font-family:'Manrope',sans-serif;font-size:1.65rem;font-weight:800;color:var(--ink);margin-top:4px;}
.step-pill {display:inline-block;background:var(--soft);color:#36552a;padding:6px 10px;
  border-radius:20px;font-size:.75rem;font-weight:800;}
div[data-testid="stVerticalBlockBorderWrapper"] {background:#fff;border:1px solid var(--line);border-radius:17px;}
div[data-testid="stMetric"] {background:#fff;border:1px solid var(--line);border-radius:15px;padding:15px 17px;}
div[data-testid="stMetric"] label {color:#718078!important;font-weight:700;}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {color:var(--ink)!important;font-family:'Manrope';font-weight:800;}
.stTextInput input,.stTextArea textarea,.stNumberInput input {
  background:#fbfcf9!important;color:var(--ink)!important;border:1px solid #dce3da!important;
  border-radius:11px!important;
}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus {
  border-color:#86b83e!important;box-shadow:0 0 0 2px rgba(185,239,88,.25)!important;
}
.stSelectbox [data-baseweb="select"]>div,.stMultiSelect [data-baseweb="select"]>div {
  background:#fbfcf9!important;border-color:#dce3da!important;border-radius:11px!important;
}
[data-testid="stFileUploader"] {background:#f9fbf6;border:1.5px dashed #aebda8;border-radius:15px;padding:12px;}
[data-testid="stFileUploader"] * {color:var(--ink)!important;}
.stButton>button,.stDownloadButton>button {
  background:var(--green)!important;color:#1d2a1d!important;border:1px solid var(--green)!important;
  border-radius:11px!important;min-height:43px;font-weight:800!important;transition:.18s ease;
}
.stButton>button:hover,.stDownloadButton>button:hover {
  background:#a8df48!important;border-color:#a8df48!important;transform:translateY(-1px);
  box-shadow:0 7px 16px rgba(65,92,39,.13);
}
.stButton>button p,.stDownloadButton>button p {color:#1d2a1d!important;font-weight:800!important;}
.stButton>button[kind="secondary"] {background:#fff!important;border:1px solid var(--line)!important;color:var(--ink)!important;}
.stButton>button[kind="secondary"] p {color:var(--ink)!important;}
[data-testid="stExpander"] {background:#fff;border:1px solid var(--line);border-radius:13px;overflow:hidden;}
[data-testid="stExpander"] summary {font-weight:700;color:var(--ink);}
[data-testid="stAlert"] {border-radius:12px;}
[data-testid="stAlert"] p,[data-testid="stAlert"] div {color:var(--ink);}
hr {border-color:var(--line);}
.caption-note {color:var(--muted);font-size:.82rem;line-height:1.55;}
.footer {text-align:center;color:#839089;font-size:.78rem;padding:24px 0 4px;}
.footer strong {color:#43534b;}
@media(max-width:900px) {
 .block-container {padding:1.1rem 1rem 2rem;}
 .hero {padding:24px 21px;}
 .panel {padding:17px;}
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
has_syllabus = bool(st.session_state.syllabus_text)
has_analysis = bool(st.session_state.analysis)
has_questions = bool(st.session_state.questions)

if "nav_target" in st.session_state:
    st.session_state["workspace_page"] = st.session_state.pop("nav_target")

with st.sidebar:
    st.markdown("""
    <div style="padding:8px 4px 18px">
      <div style="font-size:12px;letter-spacing:2px;color:#b9ef58;font-weight:800">INDALA • ACADEMIC TOOLS</div>
      <div style="font-family:Manrope;font-size:24px;font-weight:800;margin-top:7px">Assessment<br>Studio<span style="color:#b9ef58">.</span></div>
      <div style="font-size:12px;color:#b9c7bf;margin-top:7px">AI-assisted question paper workspace</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "WORKSPACE",
        ["Overview", "1  ·  Syllabus", "2  ·  Analysis", "3  ·  Paper setup", "4  ·  Review & export"],
        label_visibility="visible",
        key="workspace_page",
    )
    st.markdown("---")
    st.markdown("**WORKFLOW STATUS**")
    steps = [
        ("Syllabus uploaded", has_syllabus),
        ("AI analysis ready", has_analysis),
        ("Question paper ready", has_questions),
    ]
    for label, done in steps:
        symbol = "●" if done else "○"
        color = "#b9ef58" if done else "#899890"
        st.markdown(f"<div style='padding:5px 0;color:{color};font-size:13px'>{symbol} &nbsp;{label}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**A QUICK REMINDER**")
    st.caption("AI-generated questions and answer keys should be reviewed by faculty before examination use.")
    st.markdown("<div style='font-size:11px;color:#83948a;padding-top:18px'>INDALA COLLEGE OF ENGINEERING<br>ACADEMIC ASSESSMENT • 2026</div>", unsafe_allow_html=True)

# =========================================================
# TOP HERO
# =========================================================
st.markdown("""
<div class="hero">
  <div class="hero-kicker">INDALA COLLEGE OF ENGINEERING &nbsp; / &nbsp; FACULTY WORKSPACE</div>
  <h1>Design better assessments.<br>In less time.</h1>
  <p>Turn a subject syllabus into a structured question paper. Analyze units, balance marks,
  align questions with Bloom’s Taxonomy, edit the output and export a print-ready PDF.</p>
  <div class="hero-chip">✦ &nbsp; AI-POWERED ASSESSMENT GENERATION</div>
</div>
""", unsafe_allow_html=True)

# API key validation
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY is missing. Add it to your .env file and restart the app.")
    st.code("GROQ_API_KEY=your_groq_api_key_here")
    st.stop()

# =========================================================
# OVERVIEW
# =========================================================
if page == "Overview":
    st.markdown('<div class="eyebrow">YOUR WORKSPACE</div><div class="page-title">Assessment dashboard</div><div class="page-subtitle">A clear view of your current question-paper workflow.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="mini-card"><div class="mini-label">Syllabus</div><div class="mini-value">{"Ready" if has_syllabus else "Pending"}</div><div class="caption-note">{"Text extracted and available" if has_syllabus else "Upload a subject PDF to begin"}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="mini-card"><div class="mini-label">AI analysis</div><div class="mini-value">{"Complete" if has_analysis else "Pending"}</div><div class="caption-note">{"Units and topics identified" if has_analysis else "Analyze the extracted syllabus"}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="mini-card"><div class="mini-label">Question paper</div><div class="mini-value">{len(st.session_state.questions) if has_questions else "—"}</div><div class="caption-note">{"Questions generated" if has_questions else "No paper generated yet"}</div></div>', unsafe_allow_html=True)
    st.markdown("")
    left, right = st.columns([1.25, .75], gap="large")
    with left:
        st.markdown('<div class="panel"><div class="eyebrow">GET STARTED</div><h3 style="margin:5px 0 8px">Your six-step workflow</h3><p class="caption-note">Move through the workspace in order. You can return to any stage using the navigation on the left.</p></div>', unsafe_allow_html=True)
        workflow = [
            ("01", "Upload syllabus", "Add the subject syllabus in PDF format."),
            ("02", "Extract content", "Read the PDF and prepare its text for AI processing."),
            ("03", "Analyze syllabus", "Identify the subject, units, topics and learning outcomes."),
            ("04", "Configure paper", "Choose difficulty, Bloom level, duration and marks distribution."),
            ("05", "Review questions", "Edit question wording, options and model answers."),
            ("06", "Export PDF", "Download the question paper, with an optional answer key."),
        ]
        for n, title, desc in workflow:
            st.markdown(f"""<div style="display:flex;gap:15px;align-items:flex-start;padding:12px 15px;margin:7px 0;background:#fff;border:1px solid #e2e7df;border-radius:13px">
            <div style="background:#edf4e5;color:#36552a;font-weight:800;padding:7px 9px;border-radius:9px">{n}</div>
            <div><div style="font-weight:800">{title}</div><div class="caption-note">{desc}</div></div></div>""", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="eyebrow">CURRENT PAPER</div><h3 style="margin:5px 0 14px">Quick summary</h3></div>', unsafe_allow_html=True)
        if st.session_state.paper_settings:
            s = st.session_state.paper_settings
            st.metric("Subject", s.get("subject", "—"))
            st.metric("Total marks", s.get("total_marks", "—"))
            st.metric("Duration", f'{s.get("duration", "—")} min')
            st.caption(f'Difficulty: {s.get("difficulty", "—")} · Bloom: {s.get("bloom_level", "—")}')
        else:
            st.info("Your paper details will appear here after question generation.")
        if st.button("Start with syllabus  →", use_container_width=True):
            st.session_state["nav_target"] = "1  ·  Syllabus"
            st.rerun()

# =========================================================
# 1 — SYLLABUS UPLOAD + EXTRACTION
# =========================================================
elif page == "1  ·  Syllabus":
    st.markdown('<div class="eyebrow">STEP 01 / SOURCE MATERIAL</div><div class="page-title">Bring your syllabus in</div><div class="page-subtitle">Upload a PDF and extract its content before asking AI to analyze it.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### Upload subject syllabus")
        st.markdown('<p class="caption-note">PDF format only. Text-based PDFs are supported; scanned PDFs may require Tesseract OCR.</p>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Choose a syllabus PDF", type=["pdf"], label_visibility="collapsed")
        if uploaded:
            st.success(f"File selected · {uploaded.name}")
            if st.button("Extract syllabus text  →", type="primary", use_container_width=True):
                with st.spinner("Reading PDF and extracting content..."):
                    try:
                        extracted_text = extract_pdf_text(uploaded)
                        if extracted_text and extracted_text.strip():
                            st.session_state.syllabus_text = extracted_text
                            st.session_state.analysis = None
                            st.session_state.questions = []
                            st.session_state.paper_settings = {}
                            st.success(f"Extraction complete · {len(extracted_text):,} characters")
                        else:
                            st.error("No text was extracted. If this is a scanned PDF, install Tesseract OCR and follow the README instructions.")
                    except Exception as exc:
                        st.error(f"PDF extraction failed: {exc}")
    if st.session_state.syllabus_text:
        st.markdown("#### Extracted content")
        st.caption(f'{len(st.session_state.syllabus_text):,} characters available for analysis.')
        st.text_area("Syllabus text", st.session_state.syllabus_text, height=250, disabled=True)
        st.download_button("Download extracted text", st.session_state.syllabus_text, "extracted_syllabus.txt", "text/plain")
        if st.button("Continue to AI analysis  →", use_container_width=True):
            st.session_state["nav_target"] = "2  ·  Analysis"
            st.rerun()

# =========================================================
# 2 — ANALYSIS
# =========================================================
elif page == "2  ·  Analysis":
    st.markdown('<div class="eyebrow">STEP 02 / UNDERSTAND THE CONTENT</div><div class="page-title">Analyze your syllabus</div><div class="page-subtitle">Let AI organize the syllabus into subject details, units, topics and learning outcomes.</div>', unsafe_allow_html=True)
    if not st.session_state.syllabus_text:
        st.warning("Upload and extract a syllabus PDF first.")
    else:
        with st.container(border=True):
            st.markdown("### Syllabus intelligence")
            st.caption("The analysis uses the extracted syllabus text as its source.")
            if st.button("Run AI syllabus analysis", type="primary", use_container_width=True):
                try:
                    with st.spinner("Identifying subject, units, topics and learning outcomes..."):
                        st.session_state.analysis = analyze_syllabus(st.session_state.syllabus_text, api_key)
                    st.success("Syllabus analysis completed.")
                except Exception as exc:
                    st.error(f"Syllabus analysis failed: {exc}")
        if st.session_state.analysis:
            analysis = st.session_state.analysis
            st.markdown("#### Analysis result")
            st.markdown(f'<div class="panel"><div class="eyebrow">IDENTIFIED SUBJECT</div><div style="font-family:Manrope;font-size:1.5rem;font-weight:800">{analysis.get("subject_name", "Not identified")}</div><div class="caption-note">{analysis.get("description", "")}</div></div>', unsafe_allow_html=True)
            units = analysis.get("units", [])
            if units:
                for idx, unit_data in enumerate(units):
                    with st.expander(unit_data.get("unit_name", f"Unit {idx + 1}"), expanded=(idx == 0)):
                        a, b = st.columns(2, gap="large")
                        with a:
                            st.markdown("**Topics**")
                            for topic in unit_data.get("topics", []):
                                st.markdown(f"- {topic}")
                        with b:
                            st.markdown("**Learning outcomes**")
                            for outcome in unit_data.get("learning_outcomes", []):
                                st.markdown(f"- {outcome}")
            else:
                st.info("No units were identified in the analysis result.")
            if st.button("Continue to paper setup  →", use_container_width=True):
                st.session_state["nav_target"] = "3  ·  Paper setup"
                st.rerun()

# =========================================================
# 3 — QUESTION PAPER SETUP
# =========================================================
elif page == "3  ·  Paper setup":
    st.markdown('<div class="eyebrow">STEP 03 / BUILD YOUR ASSESSMENT</div><div class="page-title">Configure the question paper</div><div class="page-subtitle">Set the academic parameters and balance the question distribution.</div>', unsafe_allow_html=True)
    if not st.session_state.syllabus_text:
        st.warning("Upload and extract a syllabus PDF before configuring a paper.")
    else:
        with st.container(border=True):
            st.markdown("### Paper details")
            c1, c2 = st.columns(2, gap="large")
            with c1:
                subject = st.text_input("Subject name", value=(st.session_state.analysis or {}).get("subject_name", ""), placeholder="e.g. Artificial Intelligence")
                unit = st.text_input("Unit or topic to assess", placeholder="e.g. Unit 1 – Introduction to Machine Learning")
                difficulty = st.selectbox("Difficulty level", ["Easy", "Medium", "Hard"], index=1)
            with c2:
                bloom = st.selectbox("Bloom's Taxonomy level", BLOOM_LEVELS, index=2)
                duration = st.number_input("Exam duration (minutes)", min_value=15, max_value=300, value=60, step=5)
            st.markdown("---")
            st.markdown("### Question distribution")
            st.caption("Set the number of questions and marks per question. Use zero to skip a question type.")
            defaults_by_type = {"MCQ": (5, 1), "Short Answer": (3, 2), "Long Answer": (2, 5), "Case Study": (0, 10)}
            section_configs = []
            cols = st.columns(4, gap="medium")
            for idx, qtype in enumerate(QUESTION_TYPES):
                with cols[idx]:
                    st.markdown(f"**{qtype}**")
                    count = st.number_input("Number", min_value=0, max_value=20, value=defaults_by_type[qtype][0], key=f"count_{qtype}")
                    marks = st.number_input("Marks each", min_value=1, max_value=50, value=defaults_by_type[qtype][1], key=f"marks_{qtype}")
                    if count:
                        section_configs.append({"type": qtype, "count": int(count), "marks": int(marks)})
            total_questions = sum(x["count"] for x in section_configs)
            total_marks = sum(x["count"] * x["marks"] for x in section_configs)
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Questions", total_questions)
            m2.metric("Total marks", total_marks)
            m3.metric("Duration", f"{duration} min")
            generate_clicked = st.button("Generate question paper  ✦", type="primary", use_container_width=True)
        if generate_clicked:
            if not subject.strip():
                st.error("Enter a subject name.")
            elif not unit.strip():
                st.error("Enter a unit or topic.")
            elif not section_configs:
                st.error("Choose at least one question type.")
            else:
                try:
                    with st.spinner("Generating questions. This may take a little time..."):
                        generated = generate_questions(
                            syllabus_text=st.session_state.syllabus_text,
                            subject=subject.strip(),
                            unit=unit.strip(),
                            difficulty=difficulty,
                            bloom_level=bloom,
                            sections=section_configs,
                            api_key=api_key,
                        )
                    errors, actual_marks = validate_questions(generated, section_configs)
                    if errors:
                        st.session_state.questions = []
                        st.error("The generated paper did not pass validation:")
                        for error in errors:
                            st.write(f"- {error}")
                        st.caption("Try generating again or reduce the number of questions.")
                    else:
                        st.session_state.questions = generated
                        st.session_state.paper_settings = {
                            "subject": subject.strip(),
                            "duration": int(duration),
                            "total_marks": actual_marks,
                            "difficulty": difficulty,
                            "bloom_level": bloom,
                            "unit": unit.strip(),
                        }
                        st.success("Question paper generated and basic structure validated.")
                        st.session_state["nav_target"] = "4  ·  Review & export"
                        st.rerun()
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")

# =========================================================
# 4 — REVIEW, ANSWER KEY, EXPORT
# =========================================================
elif page == "4  ·  Review & export":
    st.markdown('<div class="eyebrow">STEP 04 / FINALIZE & PUBLISH</div><div class="page-title">Review your question paper</div><div class="page-subtitle">Make final edits, inspect the answer key and export a PDF.</div>', unsafe_allow_html=True)
    if not st.session_state.questions:
        st.warning("Generate a question paper first.")
    else:
        questions = st.session_state.questions
        settings = st.session_state.paper_settings
        a, b, c = st.columns(3)
        a.metric("Subject", settings.get("subject", "—"))
        b.metric("Questions", len(questions))
        c.metric("Total marks", settings.get("total_marks", "—"))
        st.markdown("### Edit questions")
        st.caption("Changes made in these fields are included in the exported PDF.")
        for i, question in enumerate(questions):
            qtype = question.get("question_type", "Question")
            with st.expander(f"Q{i + 1:02d}  ·  {qtype}  ·  {question.get('marks', 0)} marks", expanded=(i == 0)):
                question["question"] = st.text_area("Question", question.get("question", ""), key=f"q_text_{i}")
                st.caption(f"Bloom's level: {question.get('bloom_level', '')}  ·  Difficulty: {question.get('difficulty', '')}")
                if qtype == "MCQ":
                    options = list(question.get("options") or [])
                    options = (options + ["", "", "", ""])[:4]
                    option_cols = st.columns(2, gap="medium")
                    for j in range(4):
                        with option_cols[j % 2]:
                            options[j] = st.text_input(f"Option {chr(65 + j)}", options[j], key=f"q_{i}_opt_{j}")
                    question["options"] = options
                    answer = question.get("correct_answer", "A")
                    question["correct_answer"] = st.selectbox("Correct option", ["A", "B", "C", "D"], index=["A", "B", "C", "D"].index(answer) if answer in ["A", "B", "C", "D"] else 0, key=f"q_{i}_answer")
                    question["explanation"] = st.text_area("Explanation", question.get("explanation", ""), key=f"q_{i}_explanation")
                else:
                    question["model_answer"] = st.text_area("Model answer / marking guidance", question.get("model_answer", ""), key=f"q_{i}_model")
        st.markdown("---")
        st.markdown("### Answer key")
        if st.checkbox("Show answer key on screen"):
            with st.container(border=True):
                for i, question in enumerate(questions):
                    st.markdown(f"**Q{i + 1}. {question.get('question', '')}**")
                    if question.get("question_type") == "MCQ":
                        st.success(f"Correct answer: {question.get('correct_answer', '')}")
                        st.write(question.get("explanation", ""))
                    else:
                        st.write(question.get("model_answer", ""))
                    if i < len(questions) - 1:
                        st.divider()
        st.markdown("---")
        st.markdown("### Export PDF")
        with st.container(border=True):
            include_answers = st.checkbox("Include answer key and model answers in this PDF", value=False)
            try:
                pdf_bytes = create_question_pdf(
                    subject=settings["subject"],
                    questions=questions,
                    duration=settings["duration"],
                    total_marks=settings["total_marks"],
                    include_answers=include_answers,
                    unit=settings.get("unit", ""),
                )
                st.download_button("Download question paper PDF  ↓", data=pdf_bytes, file_name="AI_Question_Paper.pdf", mime="application/pdf", use_container_width=True)
            except Exception as exc:
                st.error(f"PDF creation failed: {exc}")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Clear generated paper", type="secondary", use_container_width=True):
                st.session_state.questions = []
                st.session_state.paper_settings = {}
                st.rerun()

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class="footer">
  <strong>INDALA • AI ASSESSMENT STUDIO</strong><br>
  Academic assessment support · Review all AI-generated content before examination use.
</div>
""", unsafe_allow_html=True)
