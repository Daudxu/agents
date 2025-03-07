from fastapi import FastAPI, WebSocket

app = FastAPI()
uuid = "12312412341234"
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 接受客户端的 WebSocket 连接
    await websocket.accept()
    try:
        while True:
            # 接收客户端发送的消息
            data = await websocket.receive_text()
            # 向客户端发送响应消息
            await websocket.send_text(f"你发送的消息是: {data}+{uuid}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭 WebSocket 连接
        await websocket.close()
