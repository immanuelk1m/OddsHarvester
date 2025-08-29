import pandas as pd

# --- 설정 ---
# 비교할 두 파일의 경로를 정확하게 입력해주세요.
# 파일 1: 기준이 되는 파일 (이 파일에 있는 URL을 기준으로 검색)
file_path_1 = '/Users/mac/Desktop/HIPO/oddsportal/oddssc/origin/OddsHarvester/match_urls_complete/by_league/belgium/2019-2020.csv'

# 파일 2: 비교 대상 파일 (이 파일에 URL이 없는 경우를 찾음)
file_path_2 = '/Users/mac/Desktop/HIPO/oddsportal/oddssc/origin/OddsHarvester/data/belgium-jupiler-pro-league_2019_2020_3.5.csv'

# 비교할 컬럼 이름
column_to_compare = 'match_url'
# --- 설정 끝 ---

def find_missing_urls(file1, file2, column_name):
    """
    두 CSV 파일을 비교하여 첫 번째 파일에만 존재하는 특정 컬럼의 값을 찾습니다.

    :param file1: str, 기준 파일 경로
    :param file2: str, 비교 대상 파일 경로
    :param column_name: str, 비교할 컬럼의 이름
    """
    try:
        # 1. 두 CSV 파일을 Pandas DataFrame으로 읽어옵니다.
        print(f"'{file1}' 파일 로딩 중...")
        df1 = pd.read_csv(file1)
        
        print(f"'{file2}' 파일 로딩 중...")
        df2 = pd.read_csv(file2)
        print("-" * 30)

        # 2. 각 파일에 비교할 컬럼이 있는지 확인합니다.
        if column_name not in df1.columns:
            print(f"오류: '{file1}' 파일에 '{column_name}' 컬럼이 없습니다.")
            return
        if column_name not in df2.columns:
            print(f"오류: '{file2}' 파일에 '{column_name}' 컬럼이 없습니다.")
            return

        # 3. 각 DataFrame에서 비교할 컬럼의 값들을 추출합니다.
        #    set으로 변환하여 비교 속도를 높입니다.
        urls_in_file1 = set(df1[column_name].dropna())
        urls_in_file2 = set(df2[column_name].dropna())

        # 4. 첫 번째 파일의 URL 집합에서 두 번째 파일의 URL 집합을 빼서 차집합을 구합니다.
        #    이것이 바로 첫 번째 파일에만 존재하는 URL 목록입니다.
        missing_urls = urls_in_file1 - urls_in_file2

        # 5. 결과를 출력합니다.
        if not missing_urls:
            print("결과: 첫 번째 파일의 모든 match_url이 두 번째 파일에도 존재합니다.")
        else:
            print(f"총 {len(missing_urls)}개의 누락된 match_url을 찾았습니다.")
            print(f"'{file1}'에는 있지만 '{file2}'에는 없는 항목은 다음과 같습니다:")
            print("-" * 30)
            # 리스트로 변환 후 정렬하여 보기 좋게 출력
            for url in sorted(list(missing_urls)):
                print(url)

    except FileNotFoundError as e:
        print(f"파일을 찾을 수 없습니다: {e.filename}")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

# 스크립트 실행
if __name__ == "__main__":
    find_missing_urls(file_path_1, file_path_2, column_to_compare)