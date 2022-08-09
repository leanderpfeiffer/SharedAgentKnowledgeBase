FROM python:3.9
WORKDIR /app/api

COPY requirements.txt ./
RUN pip --no-cache-dir install -r requirements.txt
COPY /app/api /app/api/
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# r = requests.get("http://localhost:8000/pa/getAutomata")

