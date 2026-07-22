import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def get_default_config():
    """기본 설정값을 반환합니다."""
    return {
        "storage_root": "", 
        "theme": "dark",
        "rp_preview_studio_path": "",
        "project_sort": "modified",
        "recent_projects": [],             
        "cover_expand_on_startup": False   
    }

def load_config():
    """설정 파일을 읽어 반환합니다. 파일이 없으면 기본값을 생성하여 저장합니다."""
    if not os.path.exists(CONFIG_FILE):
        default_config = get_default_config()
        save_config(default_config)
        return default_config
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        default_config = get_default_config()
        updated = False
        
        # 누락된 키가 있는지 검사하고 추가
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                updated = True
                
        # 기존 설정(예: v1.x)에서 누락된 키가 추가되었다면 파일에도 즉시 반영(마이그레이션)
        if updated:
            save_config(config)
            print("[안내] 기존 설정 파일(config.json)을 최신 버전 형식으로 마이그레이션했습니다.")
                
        return config
    except Exception as e:
        print(f"[오류] 설정 파일을 읽는 중 문제가 발생했습니다: {e}")
        return get_default_config()

def save_config(config_data):
    """설정 데이터를 JSON 파일로 저장합니다."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"[오류] 설정 파일을 저장하는 중 문제가 발생했습니다: {e}")
        return False