FROM Python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--reload"]

EXPOSE 8000
# This Dockerfile sets up a Python 3.12 slim environment, installs dependencies from requirements.txt,
# copies the application code into the container, and runs a FastAPI app using Uvicorn on port 8000.
