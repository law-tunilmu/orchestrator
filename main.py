from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import course.routes
import transaction.routes
import uvicorn
import dotenv
import os

app =  FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(course.routes.course_router)
app.include_router(transaction.routes.transaction_router)

dotenv.load_dotenv()
if (not os.environ.get("PRODUCTION")) and (__name__ == "__main__"):
    uvicorn.run("main:app", port=8888, log_level="info")