from fastapi import FastAPI
import uvicorn
from routes import router


app = FastAPI()
app.include_router(router)


if __name__ == '__main__':
    # 0.0.0.0 不限制访问终端ip
    # 8000 服务端口号
    # reload=True 热加载
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
