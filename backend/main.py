import os
import debugpy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 启用远程调试
if os.getenv("ENABLE_DEBUGPY", "false").lower() == "true":
    debugpy.listen(("0.0.0.0", 5678))
    print("Remote debugger is listening on 0.0.0.0:5678")

app = FastAPI(
    title="AutoTest API",
    description="自动化测试平台API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to AutoTest API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[os.path.dirname(os.path.abspath(__file__))]
    ) 