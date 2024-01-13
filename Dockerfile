FROM python:3.10

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

# 
RUN python -m pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 
COPY ./my_assistant /app/my_assistant

CMD ["python", "/app/my_assistant/main.py"]
