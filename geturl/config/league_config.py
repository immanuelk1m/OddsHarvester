"""리그 설정 및 URL 패턴 정의"""

LEAGUE_CONFIGS = {
    "belgium": {
        "name": "Belgium Jupiler League",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/belgium/jupiler-league-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/belgium/jupiler-pro-league-2024-2025/results/"
        }
    },
    "switzerland": {
        "name": "Switzerland Super League",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/switzerland/super-league-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/switzerland/super-league-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/switzerland/super-league-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/switzerland/super-league-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/switzerland/super-league-2024-2025/results/"
        }
    },
    "england": {
        "name": "England Premier League",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/england/premier-league-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/england/premier-league-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/england/premier-league-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/england/premier-league-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/england/premier-league-2024-2025/results/"
        }
    },
    "italy": {
        "name": "Italy Serie A",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/italy/serie-a-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/italy/serie-a-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/italy/serie-a-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/italy/serie-a-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/italy/serie-a-2024-2025/results/"
        }
    },
    "spain": {
        "name": "Spain La Liga",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/spain/laliga-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/spain/laliga-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/spain/laliga-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/spain/laliga-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/spain/laliga-2024-2025/results/"
        }
    },
    "sweden": {
        "name": "Sweden Allsvenskan",
        "seasons": {
            "2020": "https://www.oddsportal.com/football/sweden/allsvenskan-2020/results/",
            "2021": "https://www.oddsportal.com/football/sweden/allsvenskan-2021/results/",
            "2022": "https://www.oddsportal.com/football/sweden/allsvenskan-2022/results/",
            "2023": "https://www.oddsportal.com/football/sweden/allsvenskan-2023/results/",
            "2024": "https://www.oddsportal.com/football/sweden/allsvenskan-2024/results/"
        }
    },
    "france": {
        "name": "France Ligue 1",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/france/ligue-1-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/france/ligue-1-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/france/ligue-1-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/france/ligue-1-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/france/ligue-1-2024-2025/results/"
        }
    },
    "portugal": {
        "name": "Portugal Liga",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/portugal/primeira-liga-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/portugal/liga-portugal-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/portugal/liga-portugal-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/portugal/liga-portugal-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/portugal/liga-portugal-2024-2025/results/"
        }
    },
    "norway": {
        "name": "Norway Eliteserien",
        "seasons": {
            "2020": "https://www.oddsportal.com/football/norway/eliteserien-2020/results/",
            "2021": "https://www.oddsportal.com/football/norway/eliteserien-2021/results/",
            "2022": "https://www.oddsportal.com/football/norway/eliteserien-2022/results/",
            "2023": "https://www.oddsportal.com/football/norway/eliteserien-2023/results/",
            "2024": "https://www.oddsportal.com/football/norway/eliteserien-2024/results/"
        }
    },
    "denmark": {
        "name": "Denmark Superliga",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/denmark/superliga-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/denmark/superliga-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/denmark/superliga-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/denmark/superliga-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/denmark/superliga-2024-2025/results/"
        }
    },
    "germany": {
        "name": "Germany Bundesliga",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/germany/bundesliga-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/germany/bundesliga-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/germany/bundesliga-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/germany/bundesliga-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/germany/bundesliga-2024-2025/results/"
        }
    },
    "netherlands": {
        "name": "Netherlands Eredivisie",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/netherlands/eredivisie-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/netherlands/eredivisie-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/netherlands/eredivisie-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/netherlands/eredivisie-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/netherlands/eredivisie-2024-2025/results/"
        }
    },
    "scotland": {
        "name": "Scotland Premiership",
        "seasons": {
            "2020-2021": "https://www.oddsportal.com/football/scotland/premiership-2020-2021/results/",
            "2021-2022": "https://www.oddsportal.com/football/scotland/premiership-2021-2022/results/",
            "2022-2023": "https://www.oddsportal.com/football/scotland/premiership-2022-2023/results/",
            "2023-2024": "https://www.oddsportal.com/football/scotland/premiership-2023-2024/results/",
            "2024-2025": "https://www.oddsportal.com/football/scotland/premiership-2024-2025/results/"
        }
    }
}