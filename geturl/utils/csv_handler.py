"""CSV 파일 처리 모듈"""

import csv
import os
from datetime import datetime
from collections import defaultdict


class CSVHandler:
    """CSV 파일 저장 및 관리를 담당하는 클래스"""
    
    def __init__(self, base_dir='data'):
        """CSV 핸들러 초기화
        
        Args:
            base_dir: 데이터를 저장할 기본 디렉토리
        """
        self.base_dir = base_dir
    
    @staticmethod
    def create_directory_if_not_exists(directory):
        """디렉토리가 없으면 생성"""
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def organize_data_by_country_season(self, all_data):
        """데이터를 국가/시즌별로 정리
        
        Returns:
            {country: {season: [matches]}} 형태의 딕셔너리
        """
        organized_data = defaultdict(lambda: defaultdict(list))
        
        for match in all_data:
            # 국가 정보 추출 (league에서 국가 추출 또는 country 필드 사용)
            country = match.get('country', 'unknown')
            season = match['season']
            
            organized_data[country][season].append(match)
        
        return organized_data
    
    def save_by_country_and_season(self, all_data):
        """국가/시즌별로 개별 CSV 파일 저장"""
        # 기본 데이터 디렉토리 생성
        self.create_directory_if_not_exists(self.base_dir)
        
        # 데이터를 국가/시즌별로 정리
        organized_data = self.organize_data_by_country_season(all_data)
        
        saved_files = []
        
        for country, seasons_data in organized_data.items():
            # 국가별 디렉토리 생성
            country_dir = os.path.join(self.base_dir, country)
            self.create_directory_if_not_exists(country_dir)
            
            for season, matches in seasons_data.items():
                # 파일 경로 생성
                filename = os.path.join(country_dir, f"{season}.csv")
                
                # CSV 파일 저장
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['league', 'season', 'match_url']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for match in matches:
                        writer.writerow({
                            'league': match['league'],
                            'season': match['season'],
                            'match_url': match.get('match_url', match.get('url', ''))
                        })
                
                saved_files.append(filename)
                print(f"  저장됨: {filename} ({len(matches)}개 경기)")
        
        return saved_files
    
    @staticmethod
    def save_to_csv(all_data, filename=None):
        """수집된 데이터를 CSV 파일로 저장 (레거시 호환성)"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"all_match_urls_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['league', 'season', 'match_url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            if all_data:  # 데이터가 있을 경우에만 쓰기
                for match in all_data:
                    writer.writerow({
                        'league': match['league'],
                        'season': match['season'],
                        'match_url': match.get('match_url', match.get('url', ''))
                    })
        
        print(f"\n데이터가 {filename}에 저장되었습니다.")
        return filename
    
    @staticmethod
    def generate_statistics(all_match_data):
        """수집된 데이터의 통계 생성"""
        league_stats = {}
        for match in all_match_data:
            key = f"{match['league']} - {match['season']}"
            league_stats[key] = league_stats.get(key, 0) + 1
        
        return league_stats
    
    @staticmethod
    def print_summary(all_match_data, start_time):
        """수집 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("수집 완료 요약:")
        print("=" * 80)
        
        # 리그별 통계 출력
        league_stats = CSVHandler.generate_statistics(all_match_data)
        for key in sorted(league_stats.keys()):
            print(f"{key}: {league_stats[key]}개 경기")
        
        # 총 수집 정보
        print(f"\n총 수집된 경기 수: {len(all_match_data)}개")
        
        # 소요 시간
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n소요 시간: {duration}")
        print(f"수집 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")