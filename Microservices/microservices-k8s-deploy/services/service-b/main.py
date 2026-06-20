from fastapi import FastAPI
import socket

app = FastAPI()
HOSTNAME = socket.gethostname()

TAX_TABLE = {"IN": 18, "US": 8, "EU": 20}

@app.get("/tax")
async def tax(country: str = "DEFAULT"):
    country = country.upper()
    tax_rate = TAX_TABLE.get(country, 10)

    return {
        "service": "B",
        "country": country,
        "tax": tax_rate,
        "container": HOSTNAME,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)