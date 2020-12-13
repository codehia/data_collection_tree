FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app

# ENTRYPOINT ["uvicorn", "main:app", "--reload"]
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000

