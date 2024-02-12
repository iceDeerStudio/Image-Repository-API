FROM python:3

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["waitress-serve", "--port=8080", "--threads=8", "--call", "app:create_app"]