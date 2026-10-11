FROM node:22-alpine AS viewer-build
WORKDIR /app/heart3d
COPY heart3d/package.json heart3d/package-lock.json ./
RUN npm ci
COPY heart3d/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py index.html config.js ./
COPY models/ ./models/
COPY --from=viewer-build /app/heart3d/dist/ ./heart3d/dist/
EXPOSE 10000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
