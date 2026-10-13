# Educational Chatbot (Gemini + Tkinter)

A desktop chatbot for an educational institution. It answers academic questions using Google's Gemini model, answers common institutional questions (office hours, library timings, exams, courses, transport fee) from a built-in knowledge base, summarizes uploaded PDF/text files, keeps a per-user chat history, and includes an admin panel for managing users.

Everything runs in a single Python file with a Tkinter GUI. There is no database or web server; data is stored in plain text files next to the script.

---

## Features

### 1. Academic-only question answering
- Questions are sent to **Gemini 2.5 Flash** with a prompt that tells the model it is an academic chatbot.
- If a question is non-academic, the model is instructed to reply: *"I'm designed to answer academic questions only."*
- Before calling the model, the bot checks two things:
  - **FAQ (exact match):** short canned replies for inputs like `hello`, `bye`, `how are you`, `what can you do`.
  - **Institutional context (keyword match):** the question is scanned for keywords and the matching fact is added to the prompt so the model can use it.

| Keywords in question | Context supplied |
|---|---|
| office, hours | Office hours: Mon-Fri, 9 AM-5 PM, Building A, Room 101 |
| library, book | Library timings (weekday / weekend) |
| exam, test | All exams start at 9 AM |
| course, subject | Available courses |
| fee, payment | Transport fee and deadline |
| anything else | General welcome message |

### 2. File summarizer
- Browse and select a `.pdf` or `.txt` file (other text-based files are read as plain text).
- PDFs are read page by page with **PyPDF2**; text files are read as UTF-8.
- The text (capped at 500,000 characters) is sent to Gemini in a single call, which returns a **5-8 bullet-point summary** (temperature 0.2, max 800 output tokens).
- Scanned PDFs with no extractable text return "No text found in the file."

### 3. Chat history
- Every question and answer is saved per user in `chat_history_<username>.txt`.
- Users can open **View Chat History** from the main menu to read their own past conversations.

### 4. Login, accounts and logging
- Username/password login screen.
- **Create Account** submits a request that goes into `pending_accounts.txt` for an admin to review.
- Banned users are blocked at login.
- Important events (login success/failure/blocked, logout, questions asked, account requests, approvals, bans) are appended to `system_logs.txt` with a timestamp and username.

### 5. Admin panel
Visible only when logged in as `admin`:

| Button | What it does |
|---|---|
| View Unanswered Questions | Shows questions saved in `unanswered_questions.txt` |
| View Pending Accounts | Shows account requests from `pending_accounts.txt` |
| Approve Account | Adds a user (username + password) to the active user list |
| Add User | Adds a user directly |
| Ban User | Blocks a user from logging in, with an optional reason (the admin cannot be banned) |
| Unban User | Removes a user from the banned list |
| View Banned Users | Lists currently banned usernames |
| View Banned Credentials | Shows the ban records saved in `banned_credentials.txt` |

---

## Requirements

- Python 3.9 or newer
- Tkinter (bundled with the standard Python installer on Windows and macOS; on Debian/Ubuntu install it with `sudo apt install python3-tk`)
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

Python packages:

```bash
pip install google-generativeai PyPDF2
```

---

## Setup and Running

1. Put the script in a folder of its own (the app creates its data files in the folder it is run from).
2. Install the packages above.
3. Open the script and set your own Gemini API key in the `API_KEY` variable near the top. **Never commit a real key to GitHub or share it** (see the security notes below).
4. Run it:

```bash
python <your_script_name>.py
```

5. Log in with one of the built-in accounts defined in the `USERS` dictionary at the top of the script (`admin`, `student`, `teacher`). Change these passwords before sharing or demoing the project.

---

## Files the App Creates

| File | Purpose |
|---|---|
| `system_logs.txt` | Audit log of logins, questions and admin actions |
| `chat_history_<username>.txt` | Each user's saved questions and answers |
| `pending_accounts.txt` | Account requests waiting for admin review |
| `banned_users.txt` | List of banned usernames (reloaded at startup) |
| `banned_credentials.txt` | Admin-entered ban records (username, password, reason) |
| `unanswered_questions.txt` | Questions the bot flagged as unanswerable |

---

## How It Works

```
User question
   │
   ├─ empty?                      → error message
   ├─ exact FAQ match?            → canned reply
   └─ otherwise
        ├─ find_context(): keyword lookup → institutional fact
        ├─ build prompt (academic-only rule + context + question)
        └─ Gemini 2.5 Flash → answer shown in chat
                              → saved to chat_history_<user>.txt
                              → logged to system_logs.txt
```

Code layout:
- **Global data:** `USERS`, `BANNED_USERS`, `FAQ`, `CONTEXT`
- **Backend functions:** `log_event`, `find_context`, `answer_question`, `summarize_file`, history and ban-list helpers
- **`ChatbotGUI` class:** login, account creation, main menu, chat, file summarizer, history viewer and admin panel screens

---

## Known Limitations

These are worth knowing before a demo or viva, and are good candidates for future work.

1. **Accounts are not persistent.** Users added or approved by the admin live only in memory (`USERS`), so they disappear when the app closes. Only the ban list is saved to disk.
2. **Approving an account is manual.** The admin sees pending requests, then retypes the username and password into the Approve dialog. It does not read from or clear `pending_accounts.txt`.
3. **Passwords are stored in plain text.** This applies to the `USERS` dictionary, `pending_accounts.txt` and `banned_credentials.txt`. Passwords should be hashed (for example with `hashlib` or `bcrypt`), and the "View Banned Credentials" feature should not store passwords at all.
4. **API key is hardcoded in the source.** It should be read from an environment variable (for example `os.environ["GEMINI_API_KEY"]`) or a `.env` file that is excluded from version control.
5. **The "academic only" rule is enforced by prompt, not by code.** The model is asked to refuse non-academic questions, but this is not guaranteed, and there is no separate classifier.
6. **Unanswered-question logging rarely triggers.** The app saves a question to `unanswered_questions.txt` only if the reply contains the phrase "cannot answer", but the refusal text in the prompt is "I'm designed to answer academic questions only", so these never match.
7. **Keyword matching is simple.** For example, any question containing "fee" or "payment" gets the transport-fee context, and the word "test" triggers the exam context.
8. **Chat has no memory.** Each question is sent independently, so follow-up questions do not see earlier turns.
9. **The GUI freezes during API calls.** Requests run on the main thread, so the window is unresponsive while waiting for Gemini.
10. **The Google SDK used (`google-generativeai`) is the older generation** of Google's Python library; newer projects should check Google's current SDK recommendation.

---

## Possible Improvements

- Store users in a hashed-password file or SQLite database and make approvals persistent
- Move the API key to an environment variable
- Add conversation memory so follow-up questions work
- Run API calls in a background thread to keep the GUI responsive
- Add a proper academic/non-academic classifier and fix the unanswered-question logging
- Let the admin approve or reject a request straight from the pending list
- Add export of chat history and summaries

---

## Tech Stack

Python · Tkinter · Google Gemini 2.5 Flash · PyPDF2
