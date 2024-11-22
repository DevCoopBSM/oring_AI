import websocket
import json
import asyncio

# WebSocket을 통해 현재 사람 수를 가져오는 함수
async def get_current_people_count():
    url = "wss://occount.bsm-aripay.kr/ws/person_count"

    # WebSocket 연결을 위한 비동기 메시지 처리 함수
    def on_message(ws, message):
        try:
            # 메시지를 JSON으로 파싱
            data = json.loads(message)
            avg_count = data.get("avg_count", 0)

            # avg_count 값을 출력
            print(f"현재 avg_count 값: {avg_count}")
            ws.close()
            return avg_count
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            ws.close()
            return 0

    def on_error(ws, error):
        print(f"Error: {error}")
        
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")

    def on_open(ws):
        print("WebSocket connection opened")

    # WebSocket 연결 설정
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # 비동기적으로 WebSocket 연결을 실행
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: ws.run_forever())
    
    return result
