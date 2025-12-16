from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from services.pdf_extraction import extract_pdf_data

app = FastAPI(title="alysa – PDF ingestion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK lokalt
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    result = extract_pdf_data(
        pdf_bytes=pdf_bytes,
        filename=file.filename
    )

    return result
