FROM python:3.13-alpine

WORKDIR /app
COPY . .
RUN mkdir -p log/ data/
RUN pip install -q -r requirements.txt
CMD ["python", "bot.py"]