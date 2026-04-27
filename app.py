# import streamlit as st
# from backend.core.image_ocr import extract_text
# from backend.agents.agent_controller import agent_controller

# from backend.core.memory import (
#     init_db,
#     create_user, authenticate_user,
#     create_session, get_sessions,
#     add_message, get_messages,
#     save_report, get_reports   #  NEW
# )

# from backend.core.llm_model import generate

# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet

# import io

# # ----------------------------
# # INIT
# # ----------------------------
# init_db()
# st.set_page_config(page_title="AI Medical Assistant", layout="wide")

# # ----------------------------
# # AUTH
# # ----------------------------
# if "user" not in st.session_state:
#     st.session_state.user = None

# if st.session_state.user is None:

#     st.title(" Login / Signup")

#     mode = st.radio("Select Mode", ["Login", "Signup"])
#     user_id = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button(mode):
#         if mode == "Signup":
#             if create_user(user_id, password):
#                 st.success("User created. Please login.")
#             else:
#                 st.error("User already exists")
#         else:
#             if authenticate_user(user_id, password):
#                 st.session_state.user = user_id
#                 st.rerun()
#             else:
#                 st.error("Invalid credentials")

#     st.stop()

# # ----------------------------
# # MAIN
# # ----------------------------
# user_id = st.session_state.user
# st.title(f" AI Medical Assistant ({user_id})")

# # ----------------------------
# # SIDEBAR
# # ----------------------------
# with st.sidebar:

#     st.title(" Settings")

#     user_level = st.selectbox(
#         "User Level",
#         ["Beginner", "Medical Student", "Doctor", "Researcher"]
#     )

#     manual_mode = st.selectbox(
#         "Manual Mode Override",
#         ["Auto", "Normal", "Doctor", "Exam", "Research"]
#     )

#     st.title(" Chats")

#     sessions = get_sessions(user_id)
#     session_map = {f"{s[0]} - {s[1]}": s[0] for s in sessions}

#     selected = st.selectbox("Select Chat", list(session_map.keys()) if sessions else [])

#     if st.button("➕ New Chat"):
#         st.session_state.session_id = create_session(user_id)
#         st.rerun()

#     if selected:
#         st.session_state.session_id = session_map[selected]

#     if "session_id" not in st.session_state:
#         st.session_state.session_id = create_session(user_id)

# # ----------------------------
# # CHAT DISPLAY
# # ----------------------------
# session_id = st.session_state.get("session_id")
# messages = get_messages(session_id)

# for msg in messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # ----------------------------
# # FILE UPLOAD
# # ----------------------------
# file = st.file_uploader("Upload report", type=["pdf", "png", "jpg"])
# report_text = extract_text(file) if file else ""

# #  SAVE REPORT
# if report_text:
#     save_report(session_id, report_text)

# # ----------------------------
# #  PATIENT DASHBOARD
# # ----------------------------
# st.subheader(" Patient Dashboard")

# reports = get_reports(session_id)

# st.write(f"Total Reports Uploaded: {len(reports)}")

# if reports:
#     for i, r in enumerate(reports[:3]):
#         st.text_area(f"Report {i+1}", r[:300], height=100)

# # ----------------------------
# #  REPORT COMPARISON
# # ----------------------------
# st.subheader(" Compare Reports")

# if len(reports) >= 2:

#     r1 = st.selectbox("Select Report 1", reports, key="r1")
#     r2 = st.selectbox("Select Report 2", reports, key="r2")

#     if st.button("Compare Reports"):

#         comparison_prompt = f"""
# Compare the following two medical reports.

# Report 1:
# {r1}

# Report 2:
# {r2}

# FORMAT:

# Key Differences:
# Improvement or Worsening:
# Important Changes:
# Doctor Recommendation:
# """

#         comparison = generate("qa", comparison_prompt)

#         st.markdown("###  Comparison Result")
#         st.markdown(comparison)

# # ----------------------------
# # INPUT
# # ----------------------------
# query = st.chat_input("Ask your medical question...")

# if query and query.strip():

#     add_message(session_id, "user", query)

#     with st.chat_message("user"):
#         st.markdown(query)

#     messages = get_messages(session_id)

#     with st.chat_message("assistant"):
#         with st.spinner("Analyzing..."):

#             response = agent_controller(
#                 query,
#                 report_text,
#                 user_id,
#                 messages,
#                 user_level,
#                 manual_mode
#             )

#             st.markdown(response)

#     add_message(session_id, "assistant", response)
#     st.rerun()



