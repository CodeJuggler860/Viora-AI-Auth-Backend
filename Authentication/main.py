import sys
import os
from datetime import timedelta
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel 
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

# ── LINK TO THE AI REPOSITORY ──
viora_repo_path = r"D:\Viora-AI-master"
if viora_repo_path not in sys.path:
    sys.path.append(viora_repo_path)

# ── IMPORT OFFICIAL PREDICTORS ──
import predictor as skin_ai 
import oral_predictor as oral_ai

# ── LOCAL AUTH IMPORTS ──
from Model import User, UserCreate, UserRead, get_db, Token, TokenData
from util import get_password, verify_password, create_access_token, get_current_active_user

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Viora AI Multimodal Engines detected and loading via imports...")
    yield
    print("Shutting down Viora AI Engines...")

app = FastAPI(lifespan=lifespan)
app.mount("/outputs", StaticFiles(directory=r"D:\Viora-AI-master\gradcam_outputs"), name="outputs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SCHEMAS ──
class ChatRequest(BaseModel):
    text: str
    task: str = "general_query"
    image_type: str = ""

class PasswordReset(BaseModel):
    email: str
    new_password: str

# ── AUTH & USER ROUTES (KEEP UNTOUCHED) ──
@app.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hash_password = get_password(user.password)
    new_user = User(username=user.username, email=user.email, role=user.role, hash_password=hash_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hash_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=expire_minutes))
    return {"access_token": access_token, "token_type": "bearer"}

@app.put("/reset-password/")  
def reset_password(data: PasswordReset, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="USER NOT FOUND")
    user.hash_password = get_password(data.new_password)
    db.commit()
    return {"detail": "PASSWORD UPDATED SUCCESSFULLY"}

@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Fetches the currently logged-in user based on the JWT token."""
    return current_user

@app.delete("/users/me")
def delete_user_me(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Deletes the currently logged-in user from the database."""
    db.delete(current_user)
    db.commit()
    return {"detail": "Account successfully deleted"}

# ── THE MULTIMODAL ROUTER (FOLLOWING FRIEND'S ARCHITECTURE) ──

# Updated viora_chat in Authentication/main.py
@app.post("/viora/chat")
async def viora_chat(request: ChatRequest, current_user: User = Depends(get_current_active_user)):
    import os
    import sys
    from dotenv import load_dotenv
    
    ai_path = r"D:\Viora-AI-master"
    
    # 1. Clear caches to prevent Drive D/E conflicts
    if "Model" in sys.modules: del sys.modules["Model"]
    if "Utility" in sys.modules: del sys.modules["Utility"]
    if "Graph" in sys.modules: del sys.modules["Graph"]
    if "anonymizer" in sys.modules: del sys.modules["anonymizer"] 

    # 2. Force Path Priority to Drive D
    os.chdir(ai_path)
    if ai_path in sys.path: sys.path.remove(ai_path)
    sys.path.insert(0, ai_path)
    load_dotenv(os.path.join(ai_path, ".env"))
    
    try:
        from Graph import Workflow
        from langchain_core.messages import HumanMessage
        from anonymizer import process_input # Import from Drive D

        # --- THE PHI FILTER GATE ---
        # This cleans the text before the LangGraph Brain ever sees it
        safe_text = process_input(request.text)

        thread_id = current_user.email 
        config = {"configurable": {"thread_id": thread_id}}

        response = Workflow.invoke(
            {
                "whole_messages": [HumanMessage(content=safe_text)],
                "instruction": "You are Viora AI, a professional medical assistant.",
                "query": safe_text,
                "task": request.task,
                "image_type": request.image_type,
                "output": "",      
                "messages": []
            },
            config=config
        )
        
        # Clean up path to keep the environment stable
        sys.path.remove(ai_path)
        return {"status": "success", "text": response["output"]}

    except Exception as e:
        if ai_path in sys.path: sys.path.remove(ai_path)
        raise HTTPException(status_code=500, detail=str(e))
# ── PREDICTION ENDPOINTS (REMAINING AS BRIDGES) ──

@app.post("/viora/predict-skin")
async def viora_predict_skin(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_active_user) # Add security here
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    
    # Path manipulation for Drive D consistency
    ai_path = r"D:\Viora-AI-master"
    if "Model" in sys.modules: del sys.modules["Model"]
    if ai_path not in sys.path: sys.path.insert(0, ai_path)

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    try:
        result = skin_ai.predict(temp_path)
        return {
            "status": "success",
            "prediction": result["prediction"],
            "confidence": f"{result['confidence']:.2%}",
            "gradcam_saved_at": result["gradcam_path"],
            "model": "EfficientNet-B3 (Skin)"
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        # Restore local path priority
        if ai_path in sys.path: sys.path.remove(ai_path)

# (Oral endpoint follows the same bridge logic)
@app.post("/viora/predict-oral")
async def viora_predict_oral(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file.")
    temp_path = f"temp_oral_{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    try:
        result = oral_ai.predict(temp_path)
        return {
            "status": "success",
            "prediction": result["prediction"],
            "confidence": f"{result['confidence']:.2%}",
            "model": "Custom Oral-CNN"
        }
    except Exception as e:
        print(f"!!! ORAL PREDICTOR ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)