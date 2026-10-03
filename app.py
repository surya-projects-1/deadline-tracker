import smtplib
from email.mime.text import MIMEText
from google import genai
from google.genai import types
import streamlit as st

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]

def send_email(to_address, subject, body):
    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address
 
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key = GEMINI_API_KEY)

gemini_client = get_gemini_client()

def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])

def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])

def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"

#step1 : onboarding (username and phone)

if 'onboarded' not in st.session_state:
    st.title("📅 Deadline Tracker")
    st.caption("Upload your academic documents. Never miss a deadline.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        email_address = st.text_input(
            "Your email address",
            placeholder="you@example.com",
        )
        submitted = st.form_submit_button("Get Started 🚀")
    if submitted:
        if not name.strip() or not email_address.strip():
            st.warning("Please enter your name and email address.")
        elif(
            "@" not in email_address
            or "." not in email_address.rsplit("@", 1)[-1]
        ):
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email_address = email_address.strip()

            #activate my AI

            st.session_state.chat = gemini_client.chats.create(
                model="gemini-3.6-flash",
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()

#create a chat interface

header_col, button_col = st.columns([5,2], vertical_alignment="center")

with header_col:
    st.title("📅 Deadline Tracker")

with button_col:
    send_disabled = len(st.session_state.messages) < 1
    if st.button("Send Summary to Email", disabled=send_disabled, use_container_width=True):
        with st.spinner("Preparing your deadline summary..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
        lines = summary.strip().splitlines()

        if lines and lines[0].lower().startswith("subject:"):
            subject = lines[0].split(":", 1)[1].strip()
            body = "\n".join(lines[1:]).strip()
        else:
            subject = "Your Academic Deadline Summary"
            body = summary

        try:
            send_email(
                st.session_state.email_address,
                subject,
                body
            )

            st.success(f"Sent! Check your email: {st.session_state.email_address}")

        except Exception as error:
            st.error(f"Couldn't send that: {error}")

st.caption(
    f"Logged in as {st.session_state.name} — "
    f"updates go to {st.session_state.email_address}"
)

if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    "Ask about deadlines or attach an academic document",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "pdf"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))
    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "Analyze this academic document and extract all identifiable "
            "assignments, examinations, submission deadlines, dates, and times. "
            "Clearly flag uncertain dates. Do not invent missing information."
        )

    with st.spinner("Crunching the numbers..."):
        answer = ask_gemini(parts)
    add_message("assistant", "text", answer)