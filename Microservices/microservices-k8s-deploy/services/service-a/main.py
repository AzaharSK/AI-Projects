from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx, os, socket

app = FastAPI()

# CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
)

HOSTNAME = socket.gethostname()
TAX_SERVICE_URL = os.getenv("TAX_SERVICE_URL", "http://service-b:4000")

@app.get("/price")
async def price(amount: float = 0, country: str = "DEFAULT"):
    country = country.upper()

    async with httpx.AsyncClient() as client:
        r = await client.get(f"{TAX_SERVICE_URL}/tax", params={"country": country})
    j = r.json()

    tax = float(j.get("tax", 0))
    total = amount + tax

    return {
        "service": "A",
        "amount": amount,
        "tax": tax,
        "total": total,
        "container": HOSTNAME,
        "service_b_container": j.get("container"),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)