import google.generativeai as genai
import datetime
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import os

# Configure API
API_KEY = ""
genai.configure(api_key=API_KEY)

# ============================================================
# GLOBAL DATA
# ============================================================

USERS = {
    "admin": "password456",
    "student": "student789",
    "teacher": "teacher012"
}

BANNED_USERS = set()

FAQ = {
    "what is your name": "I am a chatbot created using Gemini API.",
    "how are you": "I'm doing great! Thank you for asking.",
    "what can you do": "I can answer FAQs, help with academic questions, and summarize files.",
    "hello": "Hello! How can I help you today?",
    "bye": "Goodbye! Have a great day!"
}

CONTEXT = {
    "office": "Office hours: Monday-Friday, 9 AM-5 PM. Building A, Room 101.",
    "library": "Library: 8 AM-10 PM weekdays, 10 AM-6 PM weekends.",
    "exams": "All exams start at 9 AM.",
    "courses": "Available courses: Mathematics, Science, History, Literature, Computer Science.",
    "transport": "Transport fee: 40,000 rupees/year. Deadline: first week of semester.",
    "general": "Welcome to our educational institution."
}

# ============================================================
# ANSWERING SYSTEM AND FILE SUMMARIZE BACKEND CODE
# ============================================================

def log_event(action, username="", detail=""):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("system_logs.txt", "a") as f:
        f.write(f"[{time}] USER: {username} | ACTION: {action} | DETAIL: {detail}\n")

def load_banned_users():
    try:
        with open("banned_users.txt", "r") as f:
            for line in f:
                if line.strip():
                    BANNED_USERS.add(line.strip())
    except:
        pass

def save_banned_users():
    with open("banned_users.txt", "w") as f:
        for user in BANNED_USERS:
            f.write(user + "\n")

def find_context(question):
    q = question.lower()
    if "office" in q or "hours" in q:
        return CONTEXT["office"]
    elif "library" in q or "book" in q:
        return CONTEXT["library"]
    elif "exam" in q or "test" in q:
        return CONTEXT["exams"]
    elif "course" in q or "subject" in q:
        return CONTEXT["courses"]
    elif "fee" in q or "payment" in q:
        return CONTEXT["transport"]
    return CONTEXT["general"]

def save_history(username, question, answer):
    with open(f"chat_history_{username}.txt", "a") as f:
        f.write(f"{'='*50}\nQuestion: {question}\nAnswer: {answer}\n{'='*50}\n\n")

def answer_question(question):
    if not question.strip():
        return "❌ Error: No question entered."
    
    if question.lower().strip() in FAQ:
        return FAQ[question.lower().strip()]
    
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        context = find_context(question)
        prompt = f"""You are an academic chatbot.
        
Institutional Context: {context}
User Question: {question}

Use the context if relevant. If non-academic, say: "I'm designed to answer academic questions only." """
        
        return model.generate_content(prompt).text
    except Exception as e:
        return f"❌ Error: {str(e)}"

def summarize_file(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    text = ""
    try:
        if file_path.lower().endswith(".pdf"):
            import PyPDF2
            pdf = PyPDF2.PdfReader(file_path)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
    if not text.strip():
        return "No text found in the file."

    # FASTEST MODEL + ONE CALL ONLY (no chunking!)
    model = genai.GenerativeModel("gemini-2.5-flash")  # Super fast & huge context

    try:
        response = model.generate_content(
            f"Summarize this in 5-8 short bullet points:\n\n{text[:500000]}",  # limit just in case
            generation_config={"temperature": 0.2, "max_output_tokens": 800}
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================================
# GUI APPLICATION
# ============================================================

class ChatbotGUI:
    def __init__(self):
        self.username = None
        self.root = tk.Tk()
        self.root.title("Gemini Chatbot System")
        self.root.geometry("700x600")
        load_banned_users()
        self.show_login()
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ============================================================
    # LOGIN & ACCOUNT CREATION
    # ============================================================
    
    def show_login(self):
        self.clear_window()
        frame = tk.Frame(self.root)
        frame.pack(expand=True)
        
        tk.Label(frame, text="LOGIN", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(frame, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(frame, width=30)
        self.username_entry.pack(pady=5)
        tk.Label(frame, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(frame, width=30, show="*")
        self.password_entry.pack(pady=5)
        
        tk.Button(frame, text="Login", command=self.login, width=20, 
                 bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(frame, text="Create Account", command=self.show_create_account, 
                 width=20).pack(pady=5)
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if username in BANNED_USERS:
            log_event("LOGIN_BLOCKED", username, "Banned user tried to login")
            messagebox.showerror("Access Denied", "Your account is banned. Contact admin.")
            return
        
        if username in USERS and USERS[username] == password:
            self.username = username
            log_event("LOGIN_SUCCESS", username)
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.show_main_menu()
        else:
            log_event("LOGIN_FAILED", username)
            messagebox.showerror("Error", "Invalid credentials!")
    
    def show_create_account(self):
        self.clear_window()
        frame = tk.Frame(self.root)
        frame.pack(expand=True)
        
        tk.Label(frame, text="CREATE ACCOUNT", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(frame, text="Username:").pack(pady=5)
        username_entry = tk.Entry(frame, width=30)
        username_entry.pack(pady=5)
        tk.Label(frame, text="Password:").pack(pady=5)
        password_entry = tk.Entry(frame, width=30, show="*")
        password_entry.pack(pady=5)
        
        def create():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            if username and password:
                with open("pending_accounts.txt", "a") as f:
                    f.write(f"{username}:{password}\n")
                log_event("ACCOUNT_REQUEST", username)
                messagebox.showinfo("Success", "Request submitted!")
                self.show_login()
            else:
                messagebox.showerror("Error", "Fill all fields!")
        
        tk.Button(frame, text="Submit", command=create, width=20, 
                 bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(frame, text="Back", command=self.show_login, width=20).pack(pady=5)
    
    # ============================================================
    # MAIN MENU
    # ============================================================
    
    def show_main_menu(self):
        self.clear_window()
        
        top = tk.Frame(self.root, bg="#2196F3", height=60)
        top.pack(fill=tk.X)
        tk.Label(top, text=f"Logged in as: {self.username}", bg="#2196F3", 
                fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=20, pady=15)
        tk.Button(top, text="Logout", command=self.logout, 
                 bg="#f44336", fg="white").pack(side=tk.RIGHT, padx=20, pady=15)
        
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(frame, text="Gemini Chatbot", font=("Arial", 18, "bold")).pack(pady=10)
        
        tk.Button(frame, text="Ask Questions", command=self.show_chat, 
                 width=30, height=2, bg="#4CAF50", fg="white", 
                 font=("Arial", 12)).pack(pady=10)
        tk.Button(frame, text="Summarize File", command=self.show_file_summarizer, 
                 width=30, height=2, bg="#2196F3", fg="white", 
                 font=("Arial", 12)).pack(pady=10)
        tk.Button(frame, text="View Chat History", command=self.show_history, 
                 width=30, height=2, bg="#FF9800", fg="white", 
                 font=("Arial", 12)).pack(pady=10)
        
        if self.username == "admin":
            tk.Button(frame, text="Admin Panel", command=self.show_admin_panel, 
                     width=30, height=2, bg="#9C27B0", fg="white", 
                     font=("Arial", 12)).pack(pady=10)
    
    def logout(self):
        log_event("LOGOUT", self.username)
        self.username = None
        self.show_login()
    
    # ============================================================
    # CHAT
    # ============================================================
    
    def show_chat(self):
        self.clear_window()
        
        top = tk.Frame(self.root, bg="#2196F3")
        top.pack(fill=tk.X)
        tk.Button(top, text="← Back", command=self.show_main_menu, 
                 bg="#1976D2", fg="white").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(top, text="Chat with Gemini", bg="#2196F3", fg="white", 
                font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.chat_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, 
                                                      height=20, state=tk.DISABLED)
        self.chat_display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.question_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.question_entry.bind("<Return>", lambda e: self.ask_question())
        
        tk.Button(input_frame, text="Send", command=self.ask_question, 
                 bg="#4CAF50", fg="white", width=10).pack(side=tk.RIGHT)
    
    def ask_question(self):
        question = self.question_entry.get().strip()
        if not question:
            return
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n🙋 You: {question}\n")
        self.chat_display.insert(tk.END, "🤖 Bot: Thinking...\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.root.update()
        
        log_event("QUESTION_ASKED", self.username, question)
        answer = answer_question(question)
        
        if "cannot answer" in answer.lower():
            with open("unanswered_questions.txt", "a") as f:
                f.write(question + "\n")
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("end-2l", "end-1l")
        self.chat_display.insert(tk.END, f"🤖 Bot: {answer}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        save_history(self.username, question, answer)
        self.question_entry.delete(0, tk.END)
    
    # ============================================================
    # FILE SUMMARIZER UI
    # ============================================================
    
    def show_file_summarizer(self):
        self.clear_window()
        
        top = tk.Frame(self.root, bg="#2196F3")
        top.pack(fill=tk.X)
        tk.Button(top, text="← Back", command=self.show_main_menu, 
                 bg="#1976D2", fg="white").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(top, text="File Summarizer", bg="#2196F3", fg="white", 
                font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=10)
        
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(frame, text="Select a file:", font=("Arial", 12)).pack(pady=10)
        
        self.file_path_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.file_path_var, width=50, 
                state='readonly').pack(pady=5)
        
        tk.Button(frame, text="Browse", command=self.browse_file, 
                 bg="#2196F3", fg="white").pack(pady=10)
        tk.Button(frame, text="Summarize", command=self.summarize, 
                 bg="#4CAF50", fg="white", width=20).pack(pady=10)
        
        tk.Label(frame, text="Summary:", font=("Arial", 12, "bold")).pack(pady=10)
        self.summary_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
        self.summary_display.pack(expand=True, fill=tk.BOTH, pady=10)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select file",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if filename:
            self.file_path_var.set(filename)


    

    
    def summarize(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Select a file first!")
            return
        
        self.summary_display.delete(1.0, tk.END)
        self.summary_display.insert(tk.END, "Summarizing...\n")
        self.root.update()
        
        summary = summarize_file(file_path)
        self.summary_display.delete(1.0, tk.END)
        self.summary_display.insert(tk.END, summary)
    
    # ============================================================
    # CHAT HISTORY
    # ============================================================
    
    def show_history(self):
        self.clear_window()
        
        top = tk.Frame(self.root, bg="#2196F3")
        top.pack(fill=tk.X)
        tk.Button(top, text="← Back", command=self.show_main_menu, 
                 bg="#1976D2", fg="white").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(top, text="Chat History", bg="#2196F3", fg="white", 
                font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=10)
        
        display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        try:
            with open(f"chat_history_{self.username}.txt", "r") as f:
                display.insert(tk.END, f.read())
        except:
            display.insert(tk.END, "No chat history found.")
    
    # ============================================================
    # ADMIN PANEL
    # ============================================================
    
    def show_admin_panel(self):
        self.clear_window()
        
        top = tk.Frame(self.root, bg="#9C27B0")
        top.pack(fill=tk.X)
        tk.Button(top, text="← Back", command=self.show_main_menu, 
                 bg="#7B1FA2", fg="white").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(top, text="Admin Panel", bg="#9C27B0", fg="white", 
                font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=10)
        
        frame = tk.Frame(self.root)
        frame.pack(expand=True)
        
        buttons = [
            ("View Unanswered Questions", self.view_unanswered, "#FF5722"),
            ("View Pending Accounts", self.view_pending, "#FF9800"),
            ("Approve Account", self.approve_account, "#4CAF50"),
            ("Add User", self.add_user, "#2196F3"),
            ("Ban User", self.ban_user, "#F44336"),
            ("Unban User", self.unban_user, "#8BC34A"),
            ("View Banned Users", self.view_banned_list, "#607D8B"),
            ("View Banned Credentials", self.view_banned_credentials, "#795548")
        ]
        
        for text, command, color in buttons:
            tk.Button(frame, text=text, command=command, width=30, height=2, 
                     bg=color, fg="white").pack(pady=5)
    
    def view_unanswered(self):
        try:
            with open("unanswered_questions.txt", "r") as f:
                content = f.read()
            messagebox.showinfo("Unanswered Questions", 
                              content if content else "No unanswered questions.")
        except:
            messagebox.showinfo("Unanswered Questions", "No file found.")
    
    def view_pending(self):
        try:
            with open("pending_accounts.txt", "r") as f:
                lines = f.readlines()
            if not lines:
                messagebox.showinfo("Pending Accounts", "No pending accounts.")
                return
            formatted = "\n".join([line.replace(":", " | Password: ") for line in lines])
            messagebox.showinfo("Pending Accounts", formatted)
        except:
            messagebox.showinfo("Pending Accounts", "No file found.")
    
    def approve_account(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Approve Account")
        dialog.geometry("300x150")
        
        tk.Label(dialog, text="Username:").pack(pady=5)
        user_entry = tk.Entry(dialog, width=30)
        user_entry.pack(pady=5)
        tk.Label(dialog, text="Password:").pack(pady=5)
        pass_entry = tk.Entry(dialog, width=30)
        pass_entry.pack(pady=5)
        
        def approve():
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            if username in USERS:
                messagebox.showerror("Error", "User exists!")
                return
            if username and password:
                USERS[username] = password
                log_event("ACCOUNT_APPROVED", "admin", username)
                messagebox.showinfo("Success", f"User '{username}' approved!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Fill all fields!")
        
        tk.Button(dialog, text="Approve", command=approve, 
                 bg="#4CAF50", fg="white").pack(pady=10)
    
    def add_user(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add User")
        dialog.geometry("300x150")
        
        tk.Label(dialog, text="Username:").pack(pady=5)
        user_entry = tk.Entry(dialog, width=30)
        user_entry.pack(pady=5)
        tk.Label(dialog, text="Password:").pack(pady=5)
        pass_entry = tk.Entry(dialog, width=30)
        pass_entry.pack(pady=5)
        
        def add():
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            if username in USERS:
                messagebox.showerror("Error", "User exists!")
                return
            if username and password:
                USERS[username] = password
                log_event("USER_ADDED", "admin", username)
                messagebox.showinfo("Success", f"User '{username}' added!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Fill all fields!")
        
        tk.Button(dialog, text="Add", command=add, 
                 bg="#2196F3", fg="white").pack(pady=10)
    
    def ban_user(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ban User")
        dialog.geometry("350x200")
        
        tk.Label(dialog, text="Username:").pack(pady=5)
        user_entry = tk.Entry(dialog, width=30)
        user_entry.pack(pady=5)
        tk.Label(dialog, text="Password:").pack(pady=5)
        pass_entry = tk.Entry(dialog, width=30, show="*")
        pass_entry.pack(pady=5)
        tk.Label(dialog, text="Reason (optional):").pack(pady=5)
        reason_entry = tk.Entry(dialog, width=30)
        reason_entry.pack(pady=5)
        
        def ban():
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            reason = reason_entry.get().strip() or "No reason"
            
            if not username or not password:
                messagebox.showerror("Error", "Enter username and password!")
                return
            if username == "admin":
                messagebox.showerror("Error", "Cannot ban admin!")
                return
            if username not in USERS:
                messagebox.showerror("Error", "User doesn't exist!")
                return
            if username in BANNED_USERS:
                messagebox.showerror("Error", "Already banned!")
                return
            
            BANNED_USERS.add(username)
            save_banned_users()
            
            with open("banned_credentials.txt", "a") as f:
                f.write(f"Username: {username} | Password: {password} | Reason: {reason}\n")
            
            log_event("USER_BANNED", "admin", f"{username} - {reason}")
            messagebox.showinfo("Success", f"User '{username}' banned!")
            dialog.destroy()
        
        tk.Button(dialog, text="Ban", command=ban, 
                 bg="#F44336", fg="white").pack(pady=10)
    
    def unban_user(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Unban User")
        dialog.geometry("300x120")
        
        tk.Label(dialog, text="Username to unban:").pack(pady=10)
        user_entry = tk.Entry(dialog, width=30)
        user_entry.pack(pady=5)
        
        def unban():
            username = user_entry.get().strip()
            if not username:
                messagebox.showerror("Error", "Enter username!")
                return
            if username not in BANNED_USERS:
                messagebox.showerror("Error", "User not banned!")
                return
            
            BANNED_USERS.remove(username)
            save_banned_users()
            log_event("USER_UNBANNED", "admin", username)
            messagebox.showinfo("Success", f"User '{username}' unbanned!")
            dialog.destroy()
        
        tk.Button(dialog, text="Unban", command=unban, 
                 bg="#8BC34A", fg="white").pack(pady=10)
    
    def view_banned_list(self):
        if not BANNED_USERS:
            messagebox.showinfo("Banned Users", "No banned users.")
            return
        banned_list = "\n".join(sorted(BANNED_USERS))
        messagebox.showinfo("Banned Users", f"Currently banned:\n\n{banned_list}")
    
    def view_banned_credentials(self):
        try:
            with open("banned_credentials.txt", "r") as f:
                content = f.read()
            if not content:
                messagebox.showinfo("Banned Credentials", "No records found.")
                return
            
            window = tk.Toplevel(self.root)
            window.title("Banned Credentials")
            window.geometry("600x400")
            
            top = tk.Frame(window, bg="#795548")
            top.pack(fill=tk.X)
            tk.Label(top, text="Banned User Credentials", bg="#795548", fg="white", 
                    font=("Arial", 14, "bold")).pack(pady=10)
            
            display = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Courier", 10))
            display.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            display.insert(tk.END, content)
            display.config(state=tk.DISABLED)
            
            tk.Button(window, text="Close", command=window.destroy, 
                     bg="#F44336", fg="white", width=15).pack(pady=10)
        except:
            messagebox.showinfo("Banned Credentials", "No records found.")
    
    def run(self):
        self.root.mainloop()

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app = ChatbotGUI()
    app.run()