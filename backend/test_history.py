# test_history_manual.py
from database import SessionLocal
import crud

db = SessionLocal()

# Use a real user_id from your users table
crud.save_message(
    db=db,
    user_id=4,             
    session_id="test-session-001",
    role="user",
    message="What is HIV?",
    input_type="text"
)

crud.save_message(
    db=db,
    user_id=4,
    session_id="test-session-001",
    role="bot",
    message="HIV is a virus that attacks the immune system...",
    input_type="text"
)

print("Done! Check /api/history in Postman.")
db.close()