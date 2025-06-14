"""
Simple FastAPI application for Azure deployment testing
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Advanced AI Agent", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Advanced AI Agent is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "Advanced AI Agent",
            "version": "1.0.0"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)