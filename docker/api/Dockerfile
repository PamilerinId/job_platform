FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get -y install libmagic1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip

RUN pip install --upgrade -r /app/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 
COPY ./.. /app/
# 
CMD ["uvicorn", "core.settings:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]