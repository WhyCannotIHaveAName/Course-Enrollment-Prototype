from fastapi import FastAPI

app = FastAPI(title="EnrollmentLab")


@app.get("/health")
def health():
    return {"status": "ok"}
