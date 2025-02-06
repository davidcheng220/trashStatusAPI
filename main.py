from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import numpy as np
import io
import json
import mysql.connector
from datetime import date

app = FastAPI()

# 設置中文字型 (根據您的系統選擇字型)
# plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # Windows 系統的字型
# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS 系統的字型

plt.rcParams['font.sans-serif'] = ['Noto Sans TC']
plt.rcParams['axes.unicode_minus'] = False  # 避免負號顯示錯誤


# 讀取資料庫配置
with open("sql.json", "r") as file:
    db_config = json.load(file)

# 連接 MySQL

def get_db_connection():
    return mysql.connector.connect(**db_config)

async def get_full_or_not(bin1: str, day: str, bin_name: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    time_ranges = [
        ('09:00:00', '10:59:59'),
        ('11:00:00', '12:59:59'),
        ('13:00:00', '14:59:59'),
        ('15:00:00', '17:00:00')
    ]
    results = []
    
    for start, end in time_ranges:
        cursor.execute(
            """
            SELECT results FROM trash_box i1
            JOIN sensor s1 ON i1.bin_id = s1.trash_box_bin_id
            WHERE i1.trash_loc = %s AND DATE(identify_time) = %s
            AND i1.bin_name = %s AND TIME(identify_time) BETWEEN %s AND %s
            ORDER BY identify_time DESC LIMIT 1;
            """,
            (bin1, day, bin_name, start, end),
        )
        data = cursor.fetchone()
        results.append(data["results"] if data else "沒滿")
    
    cursor.close()
    conn.close()
    return results

async def create_trash_plot(bin1: str, day: str, bin_name: str):
    time_intervals = ["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00"]
    full_or_not = await get_full_or_not(bin1, day, bin_name)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(time_intervals, full_or_not, marker='o', color='b', linestyle='-', linewidth=2, markersize=8)
    
    ax.set_title(f'{bin_name}', fontsize=16)
    ax.set_xlabel('時間區間', fontsize=12)
    ax.set_ylabel('狀態', fontsize=12)
    
    img_io = io.BytesIO()
    fig.savefig(img_io, format='png')
    img_io.seek(0)
    
    return img_io

@app.get("/")
async def index():
    return {"message": "Welcome to FastAPI Trash Bin API"}

@app.get("/general_status")
async def general_status(bin1: str = Query("緯育八樓"), day: str = Query('2025-01-20')):
    img_io = await create_trash_plot(bin1, day, "一般垃圾")
    return StreamingResponse(img_io, media_type="image/png")

@app.get("/recycle_status")
async def recycle_status(bin1: str = Query("緯育八樓"), day: str = Query('2025-01-20')):
    img_io = await create_trash_plot(bin1, day, "資源回收")
    return StreamingResponse(img_io, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
