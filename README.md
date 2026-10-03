# 📅 Deadline Tracker

An AI-powered academic deadline assistant that helps students extract and organize important deadlines from academic documents such as syllabuses, examination timetables, assignment sheets, and academic notices.

The application uses **Google Gemini AI** to analyze uploaded documents and generate a clear summary of upcoming academic deadlines. Students can then send the generated deadline summary directly to their email.

---

## 🚀 Features

- 📄 Upload academic documents
- 🖼️ Supports JPG, JPEG, PNG, and PDF files
- 🤖 Uses Google Gemini AI to analyze documents
- 📅 Extracts:
  - Assignments
  - Examinations
  - Submission deadlines
  - Dates
  - Times
  - Important instructions
- ⚠️ Identifies uncertain or unclear dates
- 💬 Chat-based interface for asking deadline-related questions
- 📧 Sends deadline summaries directly to the student's email
- 🔐 Uses Streamlit Secrets for API keys and email credentials
- 🎓 Designed specifically for students

---

## 🛠️ Technologies Used

- **Python**
- **Streamlit**
- **Google Gemini AI**
- **Google GenAI SDK**
- **Gmail SMTP**
- **HTML/CSS** through Streamlit UI

---

## 📂 Project Structure

```text
deadline-tracker/
│
├── app.py
├── prompts.py
├── requirements.txt
│
└── .streamlit/
    └── secrets.toml
