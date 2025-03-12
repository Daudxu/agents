from fastapi import FastAPI, WebSocket
from typing import List

app = FastAPI()

# 存储所有已连接的 WebSocket 实例
active_connections: List[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 接受客户端的 WebSocket 连接
    await websocket.accept()
    # 将新连接的 WebSocket 实例添加到列表中
    active_connections.append(websocket)
    try:
        while True:
            # 接收客户端发送的消息
            data = await websocket.receive_text()
            # 向所有已连接的客户端广播消息
            for connection in active_connections:
                await connection.send_text(f"你发送的消息是: {data}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 当连接关闭时，从列表中移除该 WebSocket 实例
        active_connections.remove(websocket)
        # 关闭 WebSocket 连接
        await websocket.close()
