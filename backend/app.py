# app.py
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routers import pokemon, etl_pipeline, pokemon_analysis


# Create FastAPI instance
app = FastAPI(title="Pokelytics Backend API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pokemon.router)
app.include_router(etl_pipeline.router)
app.include_router(pokemon_analysis.router)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI! AI Agent is ready."}

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )