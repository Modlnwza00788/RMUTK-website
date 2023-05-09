FROM python:3.10

RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
ENV PORT 8080
ENTRYPOINT ["python"]
CMD ["main.py"]