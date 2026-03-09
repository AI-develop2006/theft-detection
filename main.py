from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
import sqlite3
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Enable CORS
app.add_middleware(

    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Assets Loading
model = joblib.load('C:\\Users\\srima\\ml\\new.ipynb\\theft_model.pkl')
scaler = joblib.load('C:\\Users\\srima\\ml\\new.ipynb\\scaler.pkl')

# 2. Database Initialization
DB_PATH = 'aura_guard.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (username TEXT PRIMARY KEY, 
                       password TEXT, 
                       full_name TEXT, 
                       place TEXT, 
                       dob TEXT, 
                       mobile TEXT)''')
    # Audit history table (includes Lat/Lng for the Map)
    cursor.execute('''CREATE TABLE IF NOT EXISTS audits 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       avg_current REAL, house_size INTEGER, zero_days INTEGER, 
                       prediction INTEGER, risk_score REAL, 
                       lat REAL, lng REAL, timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_db()
@app.get("/")
def read_root():
    return {"status": "AuraGuard AI Backend is Online", "database": "Connected"}
# 3. Data 
class LoginRequest(BaseModel):
    username: str
    password: str

# --- UPDATE THE LOGIN ROUTE ---

class UserAuth(BaseModel):
    username: str
    password: str
    full_name: str
    place: str
    dob: str
    mobile: str

class ManualInputRequest(BaseModel):
    avg_current: float
    house_size: int
    zero_days: int
    # We add these so the Map knows where to put the dot
    lat: float = 13.1000  
    lng: float = 80.2707

# 4. Authentication Routes
@app.post("/signup")
def signup(user: UserAuth):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO users (username, password, full_name, place, dob, mobile) 
                          VALUES (?, ?, ?, ?, ?, ?)""", 
                       (user.username, user.password, user.full_name, user.place, user.dob, user.mobile))
        conn.commit()
        return {"message": "Account created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

@app.post("/login")
def login(user: LoginRequest):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing row["full_name"]
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user.username, user.password))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "message": "Login successful",
            "user": row["username"],
            "full_name": row["full_name"],
            "place": row["place"],
            "dob": row["dob"],
            "mobile": row["mobile"]
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

# 5. Prediction & History Routes
@app.post("/predict")
def predict_theft(data: ManualInputRequest):
    try:
        features = np.array([[data.avg_current, data.house_size, data.zero_days]])
        scaled_input = scaler.transform(features)
        
        prediction = int(model.predict(scaled_input)[0])
        try:
            score = float(model.predict_proba(scaled_input)[0][1]) * 100
        except:
            score = float(model.decision_function(scaled_input)[0])

        # --- SAVE TO DATABASE ---
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO audits 
                          (avg_current, house_size, zero_days, prediction, risk_score, lat, lng, timestamp) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (data.avg_current, data.house_size, data.zero_days, 
                        prediction, round(score, 2), data.lat, data.lng, datetime.now()))
        conn.commit()
        conn.close()

        return {
            "prediction": prediction,
            "status": "Suspicious" if prediction == 1 else "Normal",
            "risk_score": round(score, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    conn = sqlite3.connect(DB_PATH)
    # Allows us to access columns by name
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audits ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)