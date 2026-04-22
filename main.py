import os
from typing import Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from utils.prediction import predict

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI()

# Add FastAPI CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# FastAPI Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index() -> dict[str, str]:
    return {"status": "FastAPI is running!"}


@app.post('/api/v1/predict')
async def __predict__(request: Request):
    try:
        request_data: dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload.",
        )
    
    input_data = request_data.get('values')

    if input_data is None: 
        input_data = request_data['input_data'][0]
        input_data = input_data.get('values')

    if input_data is None: 
        raise HTTPException(
            status_code=400,
            detail="Invalid request syntax, `input_data` is required`",
        )
    
    else:
        predicted_values = predict(input_data)

        
    return JSONResponse(
                content=predicted_values,
                status_code=200,
            )
