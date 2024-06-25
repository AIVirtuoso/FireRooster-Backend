from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import schedule
import time
import asyncio
from contextlib import asynccontextmanager

import requests
import logging
import logging.config
from datetime import datetime, timedelta
import logging

from database import AsyncSessionLocal, create_tables
# from app.Routers import dashboard
from app.Routers import auth, scanners, stripe, alerts



app = FastAPI()

# Disable all SQLAlchemy logging
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

# app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(scanners.router, prefix="/api/scanners")
app.include_router(alerts.router, prefix="/api/alerts")
app.include_router(stripe.router, prefix="/api/stripe")


@app.get("/")
async def health_checker():
    return {"status": "success"}

# async def init():
#     print("--------------dd--------------")
#     async with AsyncSessionLocal() as db:
#         variables = await crud.get_variables(db)
#         if variables is None:
#             crud.create_variables(db)
            
#         status = await crud.get_status(db)
#         if status is None:
#             crud.create_status(db)

# async def main():
#     await create_tables()
#     await init()


# def run_scheduler():
#     # Calculate the time for the second job to start 1.5 hours after the first job
#     first_job_time = datetime.now()
#     second_job_start_time = (first_job_time + timedelta(hours=1.5)).strftime("%H:%M")

#     # Schedule jobs to run every 3 hours
#     schedule.every(3).hours.do(job, source="BuilderTrend")
#     schedule.every(3).hours.at(second_job_start_time).do(job, source="Xactanalysis")

#     # Run the scheduler in an infinite loop
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

if __name__ == "__main__":
    # asyncio.run(main())
    
    # import threading
    # scheduler_thread = threading.Thread(target=run_scheduler)
    # scheduler_thread.start()

    uvicorn.run("main:app", host="0.0.0.0", port=7000, reload=True)
