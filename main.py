from fastapi import FastAPI
from database import engine
from auth.models import Base
from auth.router import router as auth_router
from postgres_service.router import router as postgres_router
Base.metadata.create_all(bind=engine) 
app = FastAPI(title="Data Catalog API", version="0.1.0") 
app.include_router(auth_router)
app.include_router(postgres_router)  
import uvicorn

@app.get("/health")
def health():
    return {"status": "ok"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
