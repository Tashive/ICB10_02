"""
프로젝트 내의 파일 변경을 감지하여 자동으로 Git commit 및 push를 수행하는 백그라운드 동기화 스크립트입니다.
이 스크립트는 watchdog 라이브러리를 사용해 실시간으로 파일 변경 이벤트를 모니터링하며,
지정된 무시 패턴(.git, .venv, 캐시 등)을 제외한 소스코드 변경 발생 시 자동으로 Git 원격 저장소에 동기화합니다.
"""

import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class GitAutoSyncHandler(FileSystemEventHandler):
    def __init__(self, repo_path):
        super().__init__()
        self.repo_path = repo_path
        self.last_sync_time = 0
        self.cooldown = 5  # 5초 쿨다운 (빈번한 저장으로 인한 연속 커밋 방지)
        
    def on_any_event(self, event):
        if event.is_directory:
            return
            
        src_path = event.src_path
        
        # 무시할 경로 정의
        # 윈도우 경로 및 상대경로 호환성 검사
        normalized_path = os.path.normpath(src_path)
        
        # .git, .venv, .gemini 등 시스템 디렉토리 감시 제외
        ignored_keywords = [
            f"{os.sep}.git{os.sep}",
            f"{os.sep}.venv{os.sep}",
            f"{os.sep}.gemini{os.sep}",
            f"{os.sep}__pycache__{os.sep}",
            f"{os.sep}tasks{os.sep}",
            f"{os.sep}.system_generated{os.sep}",
            f"{os.sep}data{os.sep}",
        ]
        
        if any(kw in normalized_path for kw in ignored_keywords) or normalized_path.endswith('.git') or normalized_path.endswith('.venv') or normalized_path.endswith('.gemini'):
            return
            
        ignored_extensions = ['.log', '.tmp', '.bak', '.pyc', '.pyo', '.lock']
        if any(normalized_path.endswith(ext) for ext in ignored_extensions):
            return
            
        current_time = time.time()
        if current_time - self.last_sync_time >= self.cooldown:
            self.last_sync_time = current_time
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 파일 변경 감지: {normalized_path}")
            self.run_git_sync()
            
    def run_git_sync(self):
        try:
            # 변경사항 확인
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.repo_path)
            if not status.stdout.strip():
                return  # 변경사항 없음
                
            print("변경사항이 존재합니다. 자동 커밋 및 푸시를 시작합니다...")
            
            # git add
            subprocess.run(["git", "add", "."], cwd=self.repo_path)
            
            # git commit
            commit_msg = f"auto: Save changes at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.repo_path)
            
            # git push
            push_res = subprocess.run(["git", "push"], capture_output=True, text=True, cwd=self.repo_path)
            if push_res.returncode == 0:
                print("성공적으로 원격 저장소에 푸시되었습니다.")
            else:
                print(f"푸시 실패: {push_res.stderr.strip()}")
                
        except Exception as e:
            print(f"Git 동기화 중 오류 발생: {e}")

if __name__ == "__main__":
    repo_dir = r"C:\Users\tasha\OneDrive\바탕 화면\ICB10_02"
    
    print("Auto Git Sync Observer를 시작합니다...")
    handler = GitAutoSyncHandler(repo_dir)
    observer = Observer()
    observer.schedule(handler, path=repo_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
