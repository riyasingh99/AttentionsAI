from fastapi import FastAPI
from routes import auth_routes

app = FastAPI()


# Include authentication routes
app.include_router(auth_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    


