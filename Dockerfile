FROM python:3.10.11-slim

WORKDIR /app

COPY . .
COPY NotoSansTC-Regular.ttf /usr/share/fonts/truetype/NotoSansTC-Regular.ttf

# 安裝字型工具
RUN apt-get update && apt-get install -y fontconfig \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000", "--reload"]
