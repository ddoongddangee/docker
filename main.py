from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json

app = FastAPI()

DATA_FILE = "courses.json"


class Course(BaseModel):
    course_name: str
    year: str
    semester: str
    grade: str


def load_courses():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_courses(courses):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)


@app.get("/")
async def welcome() -> dict:
    return {
        "msg": "hello world?????"
    }


@app.get("/courses")
async def get_courses() -> list:
    courses = load_courses()
    return courses


@app.post("/courses")
async def add_course(course: Course) -> dict:
    courses = load_courses()
    courses.append(course.dict())
    save_courses(courses)

    return {
        "msg": "course added",
        "course": course
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)