import mysql.connector
import logging
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

# 데이터베이스 연결 설정
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
DATABASE = os.getenv('DB_NAME')

# 데이터베이스 연결 및 추천 아이템 조회
def get_recommended_items(user_code):
    connection = None
    recommended_items = []

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
            
            # 모든 사용자와 아이템 데이터를 가져오기
            query = """
                SELECT userCode, itemName
                FROM occount_kioskReceipts
            """
            cursor.execute(query)
            
            # 결과를 DataFrame으로 변환
            result = cursor.fetchall()
            if result:
                df = pd.DataFrame(result)
                logging.info("데이터를 성공적으로 가져옴")

                # 사용자별 아이템 구매 횟수 계산
                user_item_counts = df.groupby(['userCode', 'itemName']).size().reset_index(name='purchase_count')

                # 아이템-사용자 행렬 생성 (아이템이 행, 사용자가 열)
                user_item_matrix = user_item_counts.pivot(index='itemName', columns='userCode', values='purchase_count').fillna(0)

                # 코사인 유사도 계산 (사용자 간 유사도)
                cosine_sim = cosine_similarity(user_item_matrix.T)

                # 사용자별 가장 많이 구매한 아이템 3개 추출
                top_items_per_user = user_item_counts.sort_values('purchase_count', ascending=False).groupby('userCode').head(3)
                
                # 사용자가 구입한 아이템 목록을 가져오기
                user_items = top_items_per_user[top_items_per_user['userCode'] == user_code]['itemName'].tolist()
                logging.info(f"사용자가 구입한 아이템: {user_items}")

                # 사용자의 코사인 유사도 벡터를 찾기 (해당 사용자의 유사도 벡터)
                user_index = user_item_matrix.columns.get_loc(user_code)
                user_similarity = cosine_sim[user_index]

                # 유사도 높은 다른 사용자 찾기 (유사도가 높은 사용자 순)
                similar_users = np.argsort(user_similarity)[::-1]
                similar_users = similar_users[similar_users != user_index]  # 자기 자신 제외

                # 비슷한 사용자들이 구매한 아이템 추천
                recommended_items_set = set()
                for user in similar_users:
                    similar_user_code = user_item_matrix.columns[user]
                    similar_user_items = user_item_counts[user_item_counts['userCode'] == similar_user_code]['itemName'].tolist()

                    for item in similar_user_items:
                        if item not in user_items and item not in recommended_items_set:
                            recommended_items_set.add(item)
                            if len(recommended_items_set) >= 3:
                                break
                    if len(recommended_items_set) >= 3:
                        break

                recommended_items = list(recommended_items_set)
                logging.info(f"추천된 아이템: {recommended_items}")
            else:
                logging.info("데이터베이스에 아이템 정보가 없습니다.")

            cursor.close()

    except Exception as e:
        logging.error(f"데이터베이스 연결 또는 쿼리 실행 중 오류 발생: {e}")
    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            logging.info("데이터베이스 연결 종료")
    
    return recommended_items
