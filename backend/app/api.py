"""
FastAPI adapter for Phase 1 + Phase 2 resume analysis pipeline.
Thin layer that serves the frontend and routes analyze requests to the existing pipeline.
"""

import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.pipeline import analyze_resume

# Initialize FastAPI app
app = FastAPI(title="AlignHire Backend API", version="1.0.0")

# Configure CORS (localhost only for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend index.html"""
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "index.html"
    if not frontend_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    with open(frontend_path, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/api/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(default="")
):
    """
    Analyze resume against job description.
    
    Args:
        resume: Uploaded resume file (PDF, DOCX, DOC, or TXT)
        job_description: Job description text
    
    Returns:
        JSON response with analysis result from the pipeline
    """
    # Validate file extension
    file_ext = Path(resume.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported resume format. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create temporary directory for uploads
    temp_dir = Path("data/uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique temporary filename
    temp_file = temp_dir / f"temp_{resume.filename}"
    
    try:
        # Save uploaded file temporarily
        content = await resume.read()
        with open(temp_file, "wb") as f:
            f.write(content)
        
        # Call the existing analyze_resume pipeline
        result = analyze_resume(str(temp_file), job_description)
        
        return result
    
    except TypeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Resume file not found")
    except Exception as e:
        # Log the actual error for debugging
        print(f"[ERROR] Pipeline exception: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during analysis")
    
    finally:
        # Always clean up temporary file
        if temp_file.exists():
            temp_file.unlink()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "operational", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
