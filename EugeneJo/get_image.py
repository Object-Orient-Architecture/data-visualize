import os
from selenium import webdriver
import time
import folium
import warnings
import requests


warnings.filterwarnings(action="ignore")
import googlemaps
import environ

# pip install python-environ
env = environ.Env()
env.read_env()


# 장소 경위도값 알아내는 함수
def get_place_coordinates(api_key, place):
    gmaps = googlemaps.Client(key=api_key)
    try:
        autocomplete_result = gmaps.places_autocomplete(place, language="ko")
        # 장소명 자동완성 기능 사용하기
        if autocomplete_result:
            corrected_place = autocomplete_result[0]["description"]

            geocode_result = gmaps.geocode(corrected_place)

            location = geocode_result[0]["geometry"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
            return latitude, longitude
        else:
            print("장소에 대한 결과를 찾을 수 없습니다.")
            return None
    except Exception as e:
        print("오류:", e)
        return None

# 데이터를 입력받는 함수
def input_data():
    data_list = []

    print("데이터를 입력하세요(카페, 레스토랑, 음식점, 클럽, 공원, 쇼핑몰, 문화시설 등). 입력을 종료하려면 '입력종료'를 입력하세요.")

    while True:
        data = input("데이터를 입력하세요: ")

        if data.lower() == '입력종료':
            break
        else:
            data_list.append(data)

    return data_list

# 데이터를 콜하는 함수
def call_data(api_key, latitude, longitude, radius=1000, keyword=None):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'key': api_key,
        'location': f'{latitude},{longitude}',
        'radius': radius,
        'keyword': keyword
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'results' in data:
        hot_places_lat = []
        hot_places_lng = []
        for result in data['results']:
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']
            hot_places_lat.append(lat)
            hot_places_lng.append(lng)
        return hot_places_lat, hot_places_lng
    else:
        print("No places found.")
        return []



# selenium을 이용해 웹 지도를 캡쳐해서 저장하는 함수
def convert_html_to_jpg(html_file_path, output_image_path):
    # 웹드라이버 초기화
    driver = webdriver.Chrome()

    # file:// 프로토콜을 사용하여 HTML 파일 열기
    driver.get("file://" + html_file_path)

    # 렌더링 로딩 시간 주기
    time.sleep(3)

    # 스크린샷 캡처하고 JPG 파일로 저장
    driver.save_screenshot(output_image_path)

    # 웹드라이버 종료
    driver.quit()


# folium 맵을 제작
def generate_map(api_key, center, zoom_level, map_type):
    m = folium.Map(location=center, zoom_start=zoom_level, tiles=map_type)
    folium.Marker(location=center).add_to(m)
    return m


def main():
    # Google 지도 API 키 입력
    api_key = "AIzaSyCJjpyQ1_1dhC_IyXeS3Gg_BCckVmcuYx8"

    # 사용자로부터 장소, 반경, 데이터 입력 받기
    place = input("검색할 장소를 입력하세요: ")
    zoom_level_count = input("반경 정도를 입력하세요(15~20 사이 정수로 입력합니다.): ")
    data_list = input_data()

    # 위도와 경도 가져오기
    coordinates = get_place_coordinates(api_key, place)



    if coordinates is not None:
        latitude, longitude = coordinates

        hot_lat = []
        hot_lng = []
        for i in range(len(data_list)):
            lat, lng = call_data(api_key, latitude, longitude, radius=1000, keyword=data_list[i])
            hot_lat.extend(lat)
            hot_lng.extend(lng)
        
        center = [latitude, longitude]
        # Folium 맵 객체 생성
        m = generate_map(
            api_key, center, zoom_level_count, map_type="CartoDB dark_matter"
        )  # OpenStreetMap을 사용하도록 수정
        folium.Marker(location=center, popup=place).add_to(m)
        for i in range(len(hot_lat)):
            folium.CircleMarker(
                location=[hot_lat[i], hot_lng[i]],
                radius=5,  # 점의 반지름 설정
                color='blue',  # 점의 색상 설정
                fill=True,
                fill_color='blue'  # 점 내부를 채우는 색상 설정
            ).add_to(m)       
        m.save(place + ".html")

        # 파일 이름 지정하기
        current_directory = os.getcwd()
        print(current_directory)
        html_file_path = current_directory + "\\" + place + ".html"
        output_image_path = place + ".jpg"

        convert_html_to_jpg(html_file_path, output_image_path)
    else:
        print("장소의 좌표를 가져오는 데 실패했습니다.")

    print("위도:", latitude, ",", "경도: ", longitude)


# 메인 함수 실행
if __name__ == "__main__":
    main()