from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import aiohttp
import asyncio
import os

# 代理服务器的配置
PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8000
FetchURL = "https://api.open-meteo.com/v1/forecast"
app = FastAPI()
# 设置CORS
origins = [
    "http://localhost:8080",  # 允许的前端应用地址
    "http://192.168.0.4:8080",  # 允许的前端应用地址
    "http://35.160.120.126",
    "http://44.233.151.27",
    "http://34.211.200.85",
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,  # 允许的域
    allow_origins=["*"],  # 允许所有来源，或指定你的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的请求头
)
static_dir = os.path.abspath("../vue_project/distv4")
print("当前工作目录:", os.getcwd())
print("静态文件目录:", static_dir)
vue_project_dir = os.path.abspath("../vue_project")
print("vue_project 目录内容:", os.listdir(vue_project_dir))
if not os.path.exists(static_dir):
    raise RuntimeError(f"目录 '{static_dir}' 不存在")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=static_dir)
df = pd.read_csv("europe.csv")

# 定义全局变量
results = []


async def fetch_data(session, url, params=None):
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            print(f"http error: {response.status}")
            return None


async def get_temperature(session, country, city, latitude, longitude):
    params = {"latitude": latitude, "longitude": longitude, "current_weather": "true"}
    data = await fetch_data(session, FetchURL, params=params)
    if data:
        temperature = data["current_weather"]["temperature"]
        return {"city": city, "country": country, "temperature": f"{temperature}°C"}
    return None


async def update():
    global results  # 声明使用全局变量
    if results:  # 如果 results 不为空，则不执行更新
        print("Results already populated, skipping update.")
        return
    async with aiohttp.ClientSession() as session:
        tasks = []
        results = []  # 清空全局结果
        for _, row in df.iterrows():
            country = row["country"]
            capital = row["capital"]
            latitude = row["latitude"]
            longitude = row["longitude"]
            task = get_temperature(session, country, capital, latitude, longitude)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        results = [result for result in results if result is not None]  # 过滤 None 值


@app.get("/")
async def home(request: Request):
    await update()  # 更新全局 results
    print("Request URL:", request.url)
    print("Results:", results)
    context = {"request": request, "message": "服务器已连接", "data": results}
    print("Server connected")
    return templates.TemplateResponse("index.html", context, status_code=200)


@app.get("/F5")
async def F5(request: Request):
    await update()  # 更新全局 results
    context = {"request": str(request.url), "message": "数据已更新", "data": results}
    print("Data has been updated")
    return JSONResponse(content=context)


@app.post("/add")
async def add(request: Request):
    body = await request.json()
    print(body)
    capital = body.get("capital")
    country = body.get("country")
    longitude = body.get("longitude")
    latitude = body.get("latitude")

    async with aiohttp.ClientSession() as session:
        result = await get_temperature(session, country, capital, latitude, longitude)

    if result:
        results.append(result)  # 将新结果添加到全局 results
    print("Data added")
    return JSONResponse(content={"message": "数据已处理", "data": result})


@app.delete("/delete")
async def delete(request: Request):
    body = await request.json()
    city = body.get("city")
    country = body.get("country")

    global results
    # 查找要删除的项
    for index, item in enumerate(results):
        if item["city"] == city and item["country"] == country:
            del results[index]  # 删除指定的项
            print("Data deleted")
            return JSONResponse(content={"message": "数据已删除", "result": item})

    # 如果没有找到要删除的项，返回404错误
    print("No data was found to delete")
    raise HTTPException(status_code=404, detail="未找到要删除的数据")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=PROXY_HOST, port=PROXY_PORT)
