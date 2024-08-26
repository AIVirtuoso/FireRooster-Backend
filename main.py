from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text  
import uvicorn
import schedule
import time
import asyncio
from contextlib import asynccontextmanager
import aiohttp  
import requests
import logging
import logging.config
from datetime import datetime, timedelta
import logging
from aiohttp import ClientTimeout  

from database import AsyncSessionLocal, create_tables
# from app.Routers import dashboard
from app.Routers import auth, scanners, stripe, alerts, profile



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
app.include_router(profile.router, prefix="/api/profile") 


async def send_request():
    url = "http://108.61.203.106:7000/api/v1/update-alerts"  
    logging.info(f"Attempting request to {url}")  
    timeout = ClientTimeout(total=60)  # Adjust the timeout as needed  
    try:  
        async with aiohttp.ClientSession(timeout=timeout) as session:  
            # No need to capture the response; just make the request  
            async with session.get(url):  
                logging.info("Request sent successfully")  
    except aiohttp.ClientError as e:  
        logging.error(f"Client error occurred: {e}")  # Logs the error but does not raise  
    except asyncio.TimeoutError:  
        logging.error("Timeout error: The request did not complete within the configured timeout")  # Logs timeout error but does not raise  
    except Exception as e:  
        logging.error(f"Unexpected error occurred: {e}") 

async def periodic_task(interval: int):  
    while True:  
        await send_request()  
        await asyncio.sleep(interval)  

async def keep_alive():  
    """Keep the database connection alive by periodically executing a simple query."""  
    async with AsyncSessionLocal() as session:  
        while True:  
            try:  
                async with session.begin():  
                    await session.execute(text("SELECT 1"))  # Use text() for raw SQL  
                await asyncio.sleep(600)  # Sleep for 10 minutes  
            except Exception as e:  
                print(f"Error during keep-alive: {e}")  

@app.on_event("startup")  
async def startup_event():  
    # asyncio.create_task(keep_alive())  # Start the keep-alive task  
    # loop = asyncio.get_event_loop()  
    # # Schedule the periodic task to run every 1800 seconds (30 minutes)  
    # loop.create_task(periodic_task(3600)) 
    from app.Utils.remove_space import process_audio
    await process_audio("sample.mp3")

@app.get("/")
async def health_checker():
    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
