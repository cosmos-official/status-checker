#!/usr/bin/env python3
"""
Slack Notification Sender
상태 변화 정보를 받아 Slack Webhook으로 알림을 전송하는 스크립트
"""

import os
import sys
import json
import requests
from datetime import datetime

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

if not SLACK_WEBHOOK_URL:
    print("[ERROR] SLACK_WEBHOOK_URL 환경변수가 설정되어 있지 않습니다.", file=sys.stderr)
    sys.exit(1)

def build_message(change):
    emoji = ":red_circle:" if change["current_status"] == "DOWN" else ":large_green_circle:"
    status_text = f"*{change['server_name']}* 상태 변경: {change['previous_status']} → {change['current_status']}"
    time_text = f"시간: `{change['changed_at']}`"
    error_text = f"\n에러: `{change['error_message']}`" if change['error_message'] else ""
    response_time = change.get('response_time')
    response_text = f"\n응답 시간: `{response_time}ms`" if response_time is not None else ""
    return f"{emoji} {status_text}\n{time_text}{response_text}{error_text}"

def send_slack_message(text):
    payload = {"text": text}
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        if resp.status_code != 200:
            print(f"[ERROR] Slack 전송 실패: {resp.status_code} {resp.text}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"[ERROR] Slack 요청 예외: {e}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) < 2:
        print("[USAGE] send-slack-notification.py <change_json_file>", file=sys.stderr)
        sys.exit(1)
    
    change_json_file = sys.argv[1]
    if not os.path.exists(change_json_file):
        print(f"[ERROR] 파일 없음: {change_json_file}", file=sys.stderr)
        sys.exit(1)
    
    with open(change_json_file, 'r', encoding='utf-8') as f:
        changes = json.load(f)
    
    if not isinstance(changes, list):
        print("[ERROR] 입력 JSON은 리스트여야 합니다.", file=sys.stderr)
        sys.exit(1)
    
    for change in changes:
        msg = build_message(change)
        ok = send_slack_message(msg)
        if ok:
            print(f"[OK] Slack 알림 전송: {change['server_name']} {change['previous_status']} → {change['current_status']}")
        else:
            print(f"[FAIL] Slack 알림 실패: {change['server_name']}", file=sys.stderr)

if __name__ == "__main__":
    main() 