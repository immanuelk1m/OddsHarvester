"""메인 실행 스크립트 - 모든 리그의 경기 URL 수집"""

import argparse
import sys
import time
from datetime import datetime
from config.league_config import LEAGUE_CONFIGS
from scraper import SeasonProcessor
from utils import CSVHandler


def parse_arguments():
    """명령줄 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='OddsPortal 경기 URL 수집기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
사용 예시:
  # 모든 리그의 모든 시즌 수집
  python main.py
  
  # 특정 리그만 수집
  python main.py --leagues england spain italy
  
  # 특정 시즌만 수집
  python main.py --seasons 2023-2024 2024-2025
  
  # 특정 리그의 특정 시즌 수집
  python main.py --leagues england --seasons 2023-2024
  
  # 사용 가능한 리그와 시즌 목록 보기
  python main.py --list
        '''
    )
    
    parser.add_argument(
        '--leagues', '-l',
        nargs='+',
        help='수집할 리그 선택 (예: england spain italy)',
        metavar='LEAGUE'
    )
    
    parser.add_argument(
        '--seasons', '-s',
        nargs='+',
        help='수집할 시즌 선택 (예: 2023-2024 2024-2025)',
        metavar='SEASON'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='사용 가능한 리그와 시즌 목록 표시'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='data',
        help='출력 디렉토리 (기본값: data)',
        metavar='DIR'
    )
    
    return parser.parse_args()


def list_available_options():
    """사용 가능한 리그와 시즌 목록 표시"""
    print("\n" + "=" * 80)
    print("사용 가능한 리그 및 시즌")
    print("=" * 80)
    
    for country, config in LEAGUE_CONFIGS.items():
        print(f"\n리그 코드: {country}")
        print(f"리그 이름: {config['name']}")
        print("시즌:")
        for season in config['seasons'].keys():
            print(f"  - {season}")
    
    print("\n" + "=" * 80)
    print("사용법: python main.py --leagues <리그코드> --seasons <시즌>")
    print("예시: python main.py --leagues england spain --seasons 2023-2024")
    print("=" * 80)


def filter_leagues_and_seasons(selected_leagues=None, selected_seasons=None):
    """선택된 리그와 시즌으로 필터링"""
    filtered_config = {}
    
    # 리그 필터링
    if selected_leagues:
        # 대소문자 구분 없이 처리
        selected_leagues_lower = [l.lower() for l in selected_leagues]
        for country, config in LEAGUE_CONFIGS.items():
            if country.lower() in selected_leagues_lower:
                filtered_config[country] = config.copy()
    else:
        # 리그 선택이 없으면 모든 리그 포함
        filtered_config = LEAGUE_CONFIGS.copy()
    
    # 시즌 필터링
    if selected_seasons:
        for country in list(filtered_config.keys()):
            filtered_seasons = {}
            for season, url in filtered_config[country]['seasons'].items():
                if season in selected_seasons:
                    filtered_seasons[season] = url
            
            if filtered_seasons:
                filtered_config[country]['seasons'] = filtered_seasons
            else:
                # 선택된 시즌이 없는 리그는 제거
                del filtered_config[country]
    
    return filtered_config


def validate_selections(selected_leagues, selected_seasons, filtered_config):
    """선택한 리그와 시즌의 유효성 검증"""
    if selected_leagues:
        available_leagues = list(LEAGUE_CONFIGS.keys())
        invalid_leagues = [l for l in selected_leagues if l.lower() not in [al.lower() for al in available_leagues]]
        if invalid_leagues:
            print(f"\n⚠️ 잘못된 리그 코드: {', '.join(invalid_leagues)}")
            print(f"사용 가능한 리그: {', '.join(available_leagues)}")
            return False
    
    if selected_seasons:
        all_seasons = set()
        for config in LEAGUE_CONFIGS.values():
            all_seasons.update(config['seasons'].keys())
        
        invalid_seasons = [s for s in selected_seasons if s not in all_seasons]
        if invalid_seasons:
            print(f"\n⚠️ 잘못된 시즌: {', '.join(invalid_seasons)}")
            print(f"사용 가능한 시즌: {', '.join(sorted(all_seasons))}")
            return False
    
    if not filtered_config:
        print("\n⚠️ 선택한 조건에 맞는 데이터가 없습니다.")
        return False
    
    return True


def main():
    """메인 실행 함수"""
    # 명령줄 인자 파싱
    args = parse_arguments()
    
    # --list 옵션 처리
    if args.list:
        list_available_options()
        sys.exit(0)
    
    # 리그와 시즌 필터링
    filtered_config = filter_leagues_and_seasons(args.leagues, args.seasons)
    
    # 선택 유효성 검증
    if not validate_selections(args.leagues, args.seasons, filtered_config):
        sys.exit(1)
    
    # 선택된 리그와 시즌 정보 출력
    if args.leagues or args.seasons:
        print("\n" + "=" * 80)
        print("선택된 수집 대상:")
        print("=" * 80)
        
        total_leagues = len(filtered_config)
        total_seasons = sum(len(config['seasons']) for config in filtered_config.values())
        
        print(f"리그: {total_leagues}개")
        for country, config in filtered_config.items():
            print(f"  - {config['name']} ({country})")
        
        print(f"\n시즌: {total_seasons}개")
        if args.seasons:
            print(f"  선택된 시즌: {', '.join(args.seasons)}")
        else:
            print("  모든 시즌")
    
    all_match_data = []
    
    start_time = datetime.now()
    print(f"\n수집 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 시즌 프로세서 초기화
    processor = SeasonProcessor(max_pages=9, max_retries=2)
    csv_handler = CSVHandler(base_dir=args.output_dir)  # 지정된 디렉토리 사용
    
    try:
        # 필터링된 리그별로 데이터 수집
        for country, config in filtered_config.items():
            league_name = config['name']
            print(f"\n{'='*60}")
            print(f"{league_name} 처리 중...")
            print(f"{'='*60}")
            
            # 각 시즌별로 데이터 수집 (국가 정보 함께 전달)
            for season, url in config['seasons'].items():
                season_matches = processor.collect_all_matches_for_season(
                    league_name, season, url, country
                )
                all_match_data.extend(season_matches)
                time.sleep(3)  # 리그 간 대기 시간
        
        # CSV 파일을 국가/시즌별로 저장
        print("\n" + "=" * 80)
        print("데이터 저장 중...")
        print("=" * 80)
        saved_files = csv_handler.save_by_country_and_season(all_match_data)
        
        # 통계 출력
        csv_handler.print_summary(all_match_data, start_time)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단됨")
        if all_match_data:
            print("지금까지 수집된 데이터를 저장합니다...")
            csv_handler.save_by_country_and_season(all_match_data)
    except Exception as e:
        print(f"\n스크립트 실행 중 치명적인 오류 발생: {e}")
        
    finally:
        print("\n수집 프로세스 완전 종료")


if __name__ == "__main__":
    main()