import csv
import os
from datetime import datetime

def log_interaction(user_input: str, model_output: str, session_file: str = "sessions/log.csv"):
    """Generic function to append interaction to CSV with Sl. no."""
    os.makedirs("sessions", exist_ok=True)
    file_exists = os.path.isfile(session_file)
    
    sl_no = 1
    if file_exists:
        with open(session_file, 'r', encoding='utf-8') as f:
            sl_no = sum(1 for _ in f) # Sl. no is row count (includes header)

    with open(session_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Sl. no.", "Input", "Output", "Datetime"])
        
        writer.writerow([
            sl_no, 
            user_input.replace("\n", " "), 
            model_output.replace("\n", " "), 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
