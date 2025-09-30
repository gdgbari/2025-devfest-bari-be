FROM python:3.13-slim
RUN pip install uv
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN uv pip install --system --no-cache -r requirements.txt
COPY . /app
EXPOSE 8000
CMD ["python3", "/app/app.py"]
