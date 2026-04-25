import asyncio
import os
from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, model_validator
from starlette.responses import FileResponse
import httpx

load_dotenv()

app = FastAPI()
api_key_header = APIKeyHeader(name="Asteroid-Api-Key")

SECRET_API_KEY = os.environ.get("SECRET_API_KEY")
NASA_API_KEY = os.getenv("API_KEY")
NASA_URL = "https://api.nasa.gov/neo/rest/v1/feed"
LAUNCHES_URL = "https://lldev.thespacedevs.com/2.2.0/launch/previous/?limit=100"


class DatesRequest(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates_range(self):
        if self.start_date > self.end_date:
            raise ValueError("start date must be before end date")

        if (self.end_date - self.start_date).days > 7:
            raise ValueError(f"The range of days must be maximum of 7 days")


@app.get("/")
def get_index():
    return FileResponse('static/index.html')


@app.get("/api/analyze")
async def analyze(data: DatesRequest = Depends(), api_key: str = Security(api_key_header)):
    """Analyze the data from APIs and return the results"""

    if api_key != SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    nasa_params = {
        "api_key": NASA_API_KEY,
        "start_date": data.start_date.isoformat(),
        "end_date": data.end_date.isoformat()
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            task_nasa = client.get(NASA_URL, params=nasa_params)
            task_launches = client.get(LAUNCHES_URL)

            nasa_result, launches_result = await asyncio.gather(task_nasa, task_launches)

            if nasa_result.status_code != 200:
                raise HTTPException(status_code=nasa_result.status_code, detail="NASA API error")

            if launches_result.status_code != 200:
                raise HTTPException(status_code=launches_result.status_code, detail="Launches API error")

            nasa_data = nasa_result.json()
            launches_data = launches_result.json()

            total_asteroids = nasa_data.get("element_count", 0)
            hazardous_count = 0
            fastest_asteroid = None
            near_earth_objects = nasa_data.get("near_earth_objects", {})

            for day in  near_earth_objects.values():
                for asteroid in day:
                    if asteroid["is_potentially_hazardous_asteroid"]:
                        hazardous_count += 1

                    approach_data = asteroid.get("close_approach_data")
                    if not approach_data:
                        continue

                    velocity = float(asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"])

                    if fastest_asteroid is None or velocity > fastest_asteroid["velocity"]:
                        fastest_asteroid = {"name": asteroid["name"],
                                            "is_hazardous": asteroid["is_potentially_hazardous_asteroid"],
                                            "velocity": velocity
                                            }

            fun_fact = "No asteroids in this period"
            if fastest_asteroid:
                potential_hazardous_str = "potentially hazardous" if fastest_asteroid["is_hazardous"] else "safe"
                fun_fact = f"Fastest Asteroid was {fastest_asteroid['name']} with velocity {fastest_asteroid['velocity']:.2f} km/h, it was {potential_hazardous_str}."

            flight_names = []
            for flight in launches_data.get("results", []):
                flight_date = date.fromisoformat(flight["net"][:10])
                if data.start_date <= flight_date <= data.end_date:
                    flight_names.append(flight["name"])

            return {
                "total_asteroids": total_asteroids,
                "hazardous_count": hazardous_count,
                "launches": flight_names,
                "fun_fact": fun_fact
            }

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))







