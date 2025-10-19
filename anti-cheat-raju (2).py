# Anti-Cheat Monitoring System
# Generated for: goutham
# Host: raju
# Contact: gogoutham211@gmail.com
#path:\\GOUTHAM\AntiCheat_Shared\exam_questions.txt
import subprocess
import sys
import importlib
import time
import socket

# List of required modules
REQUIRED_MODULES = [
    'pyperclip',
    'keyboard',
    'smtplib',
    'email',
    'difflib',
    'datetime',
    'os'
]

def install_module(module_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        print(f"Successfully installed {module_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {module_name}: {e}")
        return False

def check_dependencies():
    print("Checking dependencies...")
    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
            print(f"{module} is already installed")
        except ImportError:
            print(f"{module} not found. Attempting to install...")
            if not install_module(module):
                print(f"Critical error: Could not install {module}")
                return False

    try:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
    except ImportError:
        print("email.mime submodules not available - should be part of standard library")
        return False

    return True

if not check_dependencies():
    print("Failed to install all required dependencies. Exiting.")
    sys.exit(1)

import pyperclip
import smtplib
import keyboard
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from difflib import SequenceMatcher
from collections import deque
import os
from datetime import datetime

# ========== CONFIGURATION ==========
QUESTIONS_FILE = r"\\GOUTHAM\AntiCheat_Shared\exam_questions.txt"
LOCAL_QUESTIONS_BACKUP = "local_backup_questions.txt"
LOG_FILE = os.path.join(os.getcwd(), "activity_log.txt")
MIN_MATCH_LENGTH = 15
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "exam.monitoring.system000@gmail.com"
EMAIL_PASSWORD = "uasz xbjc laob fdrn"
ADMIN_EMAIL = "gogoutham211@gmail.com"
BASE_SIMILARITY_THRESHOLD = 0.5
KEYSTROKE_BUFFER_SIZE = 500
KEYSTROKE_MIN_CHARS_FOR_EMAIL = 30
# ===================================
recently_detected_content = set()  # Tracks all recently detected content
MAX_RECENT_CONTENT = 100  # Maximum number of recent content items to remember
last_matched_content = {"keystrokes": "", "clipboard": ""}
sent_matches = set()
SYSTEM_HOSTNAME = socket.gethostname()



def debug_log(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] DEBUG: {message}")

# Add this global variable with other globals
last_logged_content = ""  # Tracks last logged content to prevent duplicates

def ensure_log_file():
    try:
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create new log file with header if doesn't exist
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write("=== Anti-Cheat Monitoring Log ===")
                f.write(f"System: {SYSTEM_HOSTNAME}")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            debug_log(f"Created new log file at {LOG_FILE}")
        return True
    except Exception as e:
        debug_log(f"Failed to initialize log file: {str(e)}")
        return False

def log_activity(source, content):
    try:
        global last_logged_content
        
        if not content.strip():
            return
            
        # Clean the content - keep only alphanumeric and spaces
        cleaned_content = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in content)
        cleaned_content = ' '.join(cleaned_content.split())  # Normalize spaces
        
        # Skip if content is too short or matches last logged content
        if len(cleaned_content) < MIN_MATCH_LENGTH or cleaned_content == last_logged_content:
            return
            
        last_logged_content = cleaned_content
        
        # Simple log format without timestamps or source markers
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"Detected: {cleaned_content[:500]}")  # Limit to 500 chars
            
    except Exception as e:
        debug_log(f"Failed to log activity: {str(e)}")

def send_email(subject, body):
    try:
        debug_log(f"Attempting to send email: {subject}")
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        debug_log("Email sent successfully!")
        return True
    except Exception as e:
        debug_log(f"EMAIL FAILED: {str(e)}")
        return False

def normalize_text(text):
    # Convert to lowercase and clean special characters
    text = text.lower().strip()
    text = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
    
    # Normalize spaces (replace multiple spaces with single space)
    text = ' '.join(text.split())
    
    # Keep all words regardless of length or commonality
    return text

def load_questions():
    try:
        debug_log(f"Attempting to load questions from network: {QUESTIONS_FILE}")
        if os.path.exists(QUESTIONS_FILE):
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                questions = [normalize_text(line) for line in f if line.strip()]
                debug_log(f"Loaded {len(questions)} questions from network")
                return questions
        debug_log(f"Network file not available, trying local backup: {LOCAL_QUESTIONS_BACKUP}")
        if os.path.exists(LOCAL_QUESTIONS_BACKUP):
            with open(LOCAL_QUESTIONS_BACKUP, 'r', encoding='utf-8') as f:
                questions = [normalize_text(line) for line in f if line.strip()]
                debug_log(f"Loaded {len(questions)} questions from local backup")
                return questions
        debug_log("No question files found (network or local)!")
        send_email("CRITICAL ERROR", "No exam questions file found!")
        return []
    except Exception as e:
        debug_log(f"FAILED TO LOAD QUESTIONS: {str(e)}")
        send_email("CRITICAL ERROR", f"Failed to load questions: {str(e)}")
        return []

def calculate_similarity(text1, text2):
    # Character-level similarity
    seq_char = SequenceMatcher(None, text1, text2)
    char_similarity = seq_char.ratio()
    
    # Word-level similarity
    words1 = text1.split()
    words2 = text2.split()
    seq_word = SequenceMatcher(None, words1, words2)
    word_similarity = seq_word.ratio()
    
    # Combined score (weighted more toward word similarity)
    return (char_similarity * 0.3) + (word_similarity * 0.7)

def get_similarity_threshold(text_length, source):
    """Dynamic threshold based on text length and source"""
    base_threshold = BASE_SIMILARITY_THRESHOLD
    
    # More lenient for keystrokes (since they may contain typos)
    if source == "keystrokes":
        base_threshold -= 0.05
    
    # Adjust based on length - longer texts can have lower thresholds
    length_factor = min(1.0, 100.0 / text_length)  # 100 chars gets factor of 1.0
    adjusted_threshold = base_threshold - (0.1 * (1 - length_factor))
    
    # Keep within reasonable bounds
    return max(0.05, min(0.8, adjusted_threshold))

def check_match(text, questions, source):
    global last_matched_content, recently_detected_content
    text = normalize_text(text)
    
    # Skip if content is too short (now 20 characters minimum)
    if len(text) < MIN_MATCH_LENGTH:
        debug_log(f"Ignoring short text from {source} ({len(text)} chars)")
        return False
        
    # Skip if we've recently seen this exact content
    if text in recently_detected_content:
        debug_log(f"Skipping recently detected content from {source}")
        return False
        
    log_activity(source, text)
    
    best_match = {"index": -1, "similarity": 0, "question": ""}
    match_found = False
    
    # First pass: find all matches above threshold
    matches = []
    for i, question in enumerate(questions):
        similarity = calculate_similarity(text, question)
        threshold = get_similarity_threshold(len(text), source)
        
        if similarity >= threshold:
            matches.append({
                "index": i,
                "similarity": similarity,
                "question": question
            })
    
    # If we found matches, process the best one
    if matches:
        # Sort matches by similarity (highest first)
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        best_match = matches[0]
        
        debug_log(f"MATCH FOUND with question {best_match['index']} (Similarity: {best_match['similarity']:.2f})")
        
        # Add to recently detected content
        recently_detected_content.add(text)
        # Keep the set size manageable
        if len(recently_detected_content) > MAX_RECENT_CONTENT:
            recently_detected_content.pop()
            
        email_body = (
            f"Potential match detected from {source.upper()}!\n"
            f"Hostname: {SYSTEM_HOSTNAME}\n"
            f"Typed/Copied Text:\n{text[:500]}\n\n"
            f"Best Matching Question:\n{best_match['question'][:500]}\n\n"
            f"Similarity Score: {best_match['similarity']:.2f}\n"
            f"Threshold: {get_similarity_threshold(len(text), source):.2f}\n"
            f"\nOther potential matches:\n"
        )
        
        # Add info about other matches (up to 3)
        for match in matches[1:4]:
            email_body += f"\nQuestion {match['index']}: Similarity {match['similarity']:.2f}\n"    
        send_email(f"MATCH DETECTED ({source.upper()})", email_body)
        last_matched_content[source] = text
        match_found = True
    
    # Log the best match found even if below threshold for debugging
    elif best_match["index"] != -1:
        debug_log(f"Best match below threshold: Q{best_match['index']} "
                f"(Similarity: {best_match['similarity']:.2f} vs "
                f"Threshold: {get_similarity_threshold(len(text), source):.2f})")
    
    return match_found
class KeystrokeMonitor:
    def __init__(self, questions):
        self.questions = questions
        self.buffer = deque(maxlen=KEYSTROKE_BUFFER_SIZE)
        self.last_check_time = time.time()
        self.check_interval = 2
        self.last_logged_text = ""
        self.last_sent_text = ""  # Track the last text we sent an email for

    def on_press(self, event):
        try:
            if event.name in ['shift', 'ctrl', 'alt', 'caps lock', 'tab']:
                return
            if event.name == 'backspace':
                if self.buffer:
                    self.buffer.pop()
                return
            if event.name == 'space':
                self.buffer.append(' ')
                return
            if event.name == 'enter':
                self.buffer.append('')
                return
            if len(event.name) == 1 and event.name.isprintable():
                self.buffer.append(event.name)
            current_time = time.time()
            if current_time - self.last_check_time >= self.check_interval:
                self.check_buffer()
                self.last_check_time = current_time
        except Exception as e:
            debug_log(f"Key press error: {str(e)}")

    def check_buffer(self):
        if not self.buffer:
            return
        typed_text = ''.join(self.buffer)
        if (typed_text and 
            len(typed_text) >= MIN_MATCH_LENGTH and
            typed_text != self.last_logged_text):
        
            if check_match(typed_text, self.questions, "keystrokes"):
                self.buffer.clear()  # Clear buffer after detection
            self.last_logged_text = typed_text

def main():
    if not ensure_log_file():
        debug_log("Critical: Could not initialize log file")
        send_email("LOG FILE ERROR", "Failed to initialize activity log file")

    pyperclip.copy('')
    send_email("SYSTEM STARTUP", f"Anti-Cheat system activated on host: {SYSTEM_HOSTNAME}")
    questions = load_questions()
    if not questions:
        debug_log("No questions loaded - system cannot function!")
        return

    last_clipboard_text = ""
    keystroke_monitor = KeystrokeMonitor(questions)
    keyboard.on_press(keystroke_monitor.on_press)

    try:
        debug_log("Starting monitoring...")
        while True:
            current_clipboard_text = pyperclip.paste()
            if current_clipboard_text and current_clipboard_text != last_clipboard_text:
                debug_log(f"New clipboard content detected ({len(current_clipboard_text)} chars)")
                if check_match(current_clipboard_text, questions, "clipboard"):
                    pyperclip.copy('')  # Clear clipboard after detection
                    time.sleep(2)  # Small delay to prevent rapid re-detection
                last_clipboard_text = current_clipboard_text
            time.sleep(0.5)
    except KeyboardInterrupt:
        debug_log("Shutdown requested by user")
        keyboard.unhook_all()
        send_email("SYSTEM SHUTDOWN", f"Anti-Cheat system stopped by user: {SYSTEM_HOSTNAME}")
    except Exception as e:
        debug_log(f"CRASH: {str(e)}")
        keyboard.unhook_all()
        send_email("SYSTEM CRASH", f"Anti-Cheat system crashed on {SYSTEM_HOSTNAME}:{str(e)}")
        raise

if __name__ == "__main__":
    main()

