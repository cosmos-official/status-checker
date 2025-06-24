#!/usr/bin/env python3
"""
Server Status Checker
서버 상태를 체크하고 결과를 JSON 파일로 기록하는 스크립트
"""

import json
import requests
import time
from datetime import datetime, timezone
from pathlib import Path
import sys
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServerChecker:
    def __init__(self, servers_file="data/servers.json"):
        self.servers_file = Path(servers_file)
        self.data_dir = Path("data")
        self.current_status_file = self.data_dir / "current-status.json"
        self.status_changes_file = self.data_dir / "status-changes.json"
        
        # 디렉토리 생성
        self.data_dir.mkdir(exist_ok=True)
        
        # 서버 설정 로드
        self.load_servers_config()
        
        # 현재 상태 및 변화 이력 로드
        self.load_current_status()
        self.load_status_changes()
    
    def load_servers_config(self):
        """서버 설정 파일 로드"""
        try:
            with open(self.servers_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.servers = config['servers']
            self.settings = config['settings']
            logger.info(f"서버 설정 로드 완료: {len(self.servers)}개 서버")
        except Exception as e:
            logger.error(f"서버 설정 로드 실패: {e}")
            sys.exit(1)
    
    def load_current_status(self):
        """현재 상태 파일 로드"""
        if self.current_status_file.exists():
            try:
                with open(self.current_status_file, 'r', encoding='utf-8') as f:
                    self.current_status = json.load(f)
                logger.info("현재 상태 파일 로드 완료")
            except Exception as e:
                logger.error(f"현재 상태 파일 로드 실패: {e}")
                self.current_status = {}
        else:
            self.current_status = {}
            logger.info("새로운 현재 상태 파일 생성")
    
    def load_status_changes(self):
        """상태 변화 이력 파일 로드"""
        if self.status_changes_file.exists():
            try:
                with open(self.status_changes_file, 'r', encoding='utf-8') as f:
                    self.status_changes = json.load(f)
                logger.info("상태 변화 이력 파일 로드 완료")
            except Exception as e:
                logger.error(f"상태 변화 이력 파일 로드 실패: {e}")
                self.status_changes = {"changes": []}
        else:
            self.status_changes = {"changes": []}
            logger.info("새로운 상태 변화 이력 파일 생성")
    
    def check_server(self, server):
        """개별 서버 상태 체크"""
        server_id = server['id']
        url = server['url']
        timeout = server.get('timeout', self.settings['default_timeout'])
        expected_status = server.get('expected_status', 200)
        
        start_time = time.time()
        status = "DOWN"
        response_time = None
        error_message = None
        
        try:
            response = requests.get(
                url, 
                timeout=timeout,
                headers={'User-Agent': 'Server-Status-Checker/1.0'}
            )
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            if response.status_code == expected_status:
                status = "UP"
            else:
                error_message = f"예상 상태 코드: {expected_status}, 실제: {response.status_code}"
                
        except requests.exceptions.Timeout:
            error_message = f"타임아웃 ({timeout}초)"
        except requests.exceptions.ConnectionError:
            error_message = "연결 오류"
        except requests.exceptions.RequestException as e:
            error_message = f"요청 오류: {str(e)}"
        except Exception as e:
            error_message = f"예상치 못한 오류: {str(e)}"
        
        return {
            "server_id": server_id,
            "status": status,
            "response_time": response_time,
            "error_message": error_message,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    
    def check_all_servers(self):
        """모든 서버 상태 체크"""
        logger.info("서버 상태 체크 시작")
        
        check_results = {}
        status_changes = []
        
        for server in self.servers:
            if not server.get('enabled', True):
                continue
                
            server_id = server['id']
            logger.info(f"체크 중: {server['name']} ({server['url']})")
            
            # 서버 상태 체크
            result = self.check_server(server)
            check_results[server_id] = result
            
            # 상태 변화 감지
            previous_status = self.current_status.get(server_id, {}).get('status', 'UNKNOWN')
            current_status = result['status']
            
            if previous_status != current_status:
                change_record = {
                    "server_id": server_id,
                    "server_name": server['name'],
                    "previous_status": previous_status,
                    "current_status": current_status,
                    "changed_at": result['checked_at'],
                    "response_time": result['response_time'],
                    "error_message": result['error_message']
                }
                status_changes.append(change_record)
                
                logger.info(f"상태 변화 감지: {server['name']} {previous_status} → {current_status}")
        
        # 현재 상태 업데이트
        self.current_status = check_results
        
        # 상태 변화 이력에 추가
        if status_changes:
            self.status_changes["changes"].extend(status_changes)
            logger.info(f"{len(status_changes)}개의 상태 변화 기록됨")
        
        logger.info("서버 상태 체크 완료")
        return check_results, status_changes
    
    def save_results(self):
        """결과를 파일로 저장"""
        try:
            # 현재 상태 저장
            with open(self.current_status_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_status, f, indent=2, ensure_ascii=False)
            
            # 상태 변화가 있을 때만 변화 이력 저장
            if self.status_changes["changes"]:
                with open(self.status_changes_file, 'w', encoding='utf-8') as f:
                    json.dump(self.status_changes, f, indent=2, ensure_ascii=False)
                logger.info("상태 변화 이력 저장됨")
            
            logger.info("결과 저장 완료")
            
        except Exception as e:
            logger.error(f"결과 저장 실패: {e}")
            sys.exit(1)
    
    def run(self):
        """메인 실행 함수"""
        logger.info("=== 서버 상태 체크 시작 ===")
        
        # 서버 상태 체크
        results, changes = self.check_all_servers()
        
        # 결과 저장
        self.save_results()
        
        # 요약 출력
        up_count = sum(1 for r in results.values() if r['status'] == 'UP')
        down_count = len(results) - up_count
        
        logger.info(f"=== 체크 완료 ===")
        logger.info(f"총 서버: {len(results)}개")
        logger.info(f"정상: {up_count}개")
        logger.info(f"오류: {down_count}개")
        logger.info(f"상태 변화: {len(changes)}개")
        
        return results, changes

def main():
    """메인 함수"""
    checker = ServerChecker()
    results, changes = checker.run()
    
    # 종료 코드 설정 (다운된 서버가 있으면 1, 없으면 0)
    exit_code = 1 if any(r['status'] == 'DOWN' for r in results.values()) else 0
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 