import mysql.connector
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 설정
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
DATABASE = os.getenv('DB_NAME')

# 데이터베이스 연결 및 아이템 경고 조회
def get_item_warning(user_code):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            ssl_disabled=True
        )
        
        if connection.is_connected():
            logging.info("데이터베이스에 연결됨")
            cursor = connection.cursor(dictionary=True)

            # 현재 날짜와 3주 전 날짜 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=3)

            # 3주간의 구매 데이터 조회
            query_receipts = """
            SELECT itemCode, COUNT(*) as purchase_count
            FROM occount_kioskReceipts
            WHERE userCode = %s AND saleDate BETWEEN %s AND %s
            GROUP BY itemCode
            """
            cursor.execute(query_receipts, (user_code, start_date, end_date))
            user_purchases = cursor.fetchall()

            # 구매한 아이템의 itemCode 리스트
            purchased_item_codes = [item['itemCode'] for item in user_purchases]

            # 재고가 0이 아니고 5 이하인 아이템 조회
            query_items = """
            SELECT itemId, itemName, itemQuantity
            FROM occount_items
            WHERE itemQuantity > 0 AND itemQuantity <= 5
            """
            cursor.execute(query_items)
            available_items = cursor.fetchall()

            # 조건에 맞는 아이템 필터링
            filtered_items = [
                item for item in available_items if item['itemId'] in purchased_item_codes
            ]

            # 구매한 아이템이 없거나 조건에 맞는 아이템이 없을 경우
            if not purchased_item_codes or not filtered_items:
                return ""  # 공백 반환

            # 가장 매수가 적은 아이템 찾기
            min_purchase_count = min(item['itemQuantity'] for item in filtered_items)
            candidates = [item for item in filtered_items if item['itemQuantity'] == min_purchase_count]

            if len(candidates) > 1:
                # 후보가 2개 이상일 경우, 사용자가 가장 많이 구매한 아이템 찾기
                max_purchase_count = 0
                recommended_item = None
                for candidate in candidates:
                    item_code = candidate['itemId']
                    purchase_count = next((p['purchase_count'] for p in user_purchases if p['itemCode'] == item_code), 0)
                    if purchase_count > max_purchase_count:
                        max_purchase_count = purchase_count
                        recommended_item = candidate['itemName']
                return recommended_item if recommended_item else ""
            else:
                return candidates[0]['itemName']

    except Exception as e:
        logging.error(f"데이터베이스 연결 또는 쿼리 실행 중 오류 발생: {e}")
        return ""
    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            logging.info("데이터베이스 연결 종료")
