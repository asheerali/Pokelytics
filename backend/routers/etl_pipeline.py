# routers/etl_pipeline.py
from fastapi import APIRouter
from data_processing.etl import run_etl_pipeline


router = APIRouter(
    prefix="/pokemon",
    tags=["Pokemon"]
)


@router.post("/etl/run-pipeline")
async def run_pipeline():
    print("ETL Pipeline STARTED")
    run_etl_pipeline()
    print("ETL Pipeline FINISHED")
    return {"detail": "Pipeline completed."}
