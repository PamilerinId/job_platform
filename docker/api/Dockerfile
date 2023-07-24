FROM python:3.11-slim-bookworm

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

# RUN pip install -r /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 
COPY ./.. /app/

# 
CMD ["uvicorn", "core.settings:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]