import requests

city = "Tokyo"
TOKEN = "supersecrettoken123"

# Token passed as a query parameter, headers was making it run weirdly
API_URL = f"http://34.121.28.86:5000/api/time/{city}?token={TOKEN}"

response = requests.get(API_URL)

if response.status_code == 200:
    print("✅ Success:", response.json())
else:
    print("❌ Error:", response.status_code, response.text)
