# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"message": "Hello Bhai.."}
import os
import time
import shutil
import tempfile
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fpdf import FPDF
from PIL import Image

app = FastAPI()

@app.post("/convert-to-pdf/")
async def convert_images_to_pdf(files: list[UploadFile] = File(...)):
    temp_dir = tempfile.mkdtemp()
    img_paths = []

    try:
        # Save uploaded files
        for file in files:
            img_path = os.path.join(temp_dir, file.filename)
            with open(img_path, "wb") as f:
                f.write(await file.read())
            img_paths.append(img_path)

        # Create PDF
        pdf = FPDF()
        for img_path in img_paths:
            try:
                with Image.open(img_path) as img:
                    img = img.convert("RGB")
                    temp_jpg_path = img_path + ".jpg"
                    img.save(temp_jpg_path)

                    pdf.add_page()
                    pdf.image(temp_jpg_path, x=10, y=10, w=190)
                    os.remove(temp_jpg_path)

            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                continue

        output_pdf_path = os.path.join(temp_dir, "output.pdf")
        pdf.output(output_pdf_path)

        # Stream the PDF
        pdf_stream = open(output_pdf_path, "rb")
        response = StreamingResponse(pdf_stream, media_type="application/pdf")
        response.headers["Content-Disposition"] = "attachment; filename=converted.pdf"
        return response

    except Exception as e:
        raise e

    finally:
        # Cleanup
        for path in img_paths:
            try:
                os.remove(path)
            except Exception as e:
                print(f"Could not delete {path}: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
