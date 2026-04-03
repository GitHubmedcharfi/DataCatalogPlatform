from fastapi import FastAPI
from auth.database import engine
from auth.models import Base
from auth.router import router as auth_router
Base.metadata.create_all(bind=engine) 
app = FastAPI(title="Data Catalog API", version="0.1.0") 
app.include_router(auth_router)
 
@app.get("/health")
def health():
    return {"status": "ok"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

