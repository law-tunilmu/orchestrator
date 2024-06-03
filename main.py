from fastapi import FastAPI
import course.routes

app =  FastAPI()

app.include_router(course.routes.course_router)
