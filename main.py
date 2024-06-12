from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCR
import aiofiles
import os
import uuid
from celery import Celery

app = FastAPI()

# Пути к вашим обученным моделям
det_model_dir = "/app/models/det_model"
rec_model_dir = "/app/models/rec_model"

ocr = PaddleOCR(use_angle_cls=True, det_model_dir=det_model_dir, rec_model_dir=rec_model_dir, lang='ru')

celery_app = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL'), backend=os.getenv('CELERY_RESULT_BACKEND'))

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    file_location = f"files/{uuid.uuid4()}_{file.filename}"
    
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    
    async with aiofiles.open(file_location, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    task = process_file.delay(file_location)
    return JSONResponse(status_code=202, content={"task_id": task.id, "file_url": file_location})

@celery_app.task
def process_file(file_path: str):
    result = ocr.ocr(file_path, cls=True)
    os.remove(file_path)
    return result

@app.get("/result/{task_id}")
def get_result(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == 'PENDING':
        return JSONResponse(status_code=202, content={"state": task.state, "status": "Pending..."})
    elif task.state != 'FAILURE':
        return JSONResponse(status_code=200, content={"state": task.state, "result": task.result})
    else:
        return JSONResponse(status_code=500, content={"state": task.state, "status": str(task.info)})


