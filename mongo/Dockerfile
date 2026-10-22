FROM node:20-alpine AS web
WORKDIR /web
COPY web/package.json .
RUN npm install
COPY web .
RUN npm run build

FROM python:3.12-slim
WORKDIR /srv
COPY mongo/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mongo/app ./app
COPY --from=web /web/dist ./web/dist

CMD ["sh", "-c", "python -m app.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
