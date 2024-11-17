from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import chromedriver_autoinstaller  # 추가

def get_current_people_count():
    # 자동으로 맞는 ChromeDriver 버전을 설치합니다.
    chromedriver_autoinstaller.install()

    # Chrome 옵션 설정 (브라우저를 보지 않고 실행, 성능 최적화)
    options = Options()
    options.add_argument("--headless")  # Headless 모드 (브라우저 창을 띄우지 않음)
    options.add_argument("--disable-gpu")  # GPU 가속 비활성화
    options.add_argument("--no-sandbox")  # 샌드박스 비활성화
    options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 안 함
    options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
    options.add_argument("--start-maximized")  # 최대화 모드로 시작

    # `chromedriver_autoinstaller`가 설치한 ChromeDriver 경로 자동 설정
    service = Service()

    # 웹 드라이버 시작
    driver = webdriver.Chrome(service=service, options=options)

    # 웹 페이지 요청
    url = "https://occount.bsm-aripay.kr/"
    driver.get(url)

    try:
        # WebDriverWait을 사용하여 요소가 로드될 때까지 기다림 (최대 5초)
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'sc-ZVgAE.dQAtJj'))
        )

        # 0명 텍스트 추출
        current_people_text = element.text
        print(current_people_text)  # "0명"
        
        # 텍스트에서 숫자 추출 (정규식을 사용)
        match = re.search(r'\d+', current_people_text)
        if match:
            current_people_count = int(match.group())  # 숫자로 변환
            return current_people_count
        else:
            raise ValueError("숫자를 찾을 수 없습니다. 텍스트: {}".format(current_people_text))  # 에러 발생

    finally:
        # 드라이버 종료
        driver.quit()
