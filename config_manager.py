import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def get_default_config():
    return {
        "storage_root": "", 
        "theme": "dark",
        "rp_preview_studio_path": "",
        "project_sort": "modified",
        "recent_projects": [],             
        "cover_expand_on_startup": False,
        "cover_expanded": False,
        "splitter_sizes": [220, 980]  # UI 폭 조절 기본값 추가
    }

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = get_default_config()
        save_config(default_config)
        return default_config
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        default_config = get_default_config()
        updated = False
        
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                updated = True
                
        if updated:
            save_config(config)
            print("[안내] 기존 설정 파일(config.json)을 최신 버전 형식으로 마이그레이션했습니다.")
                
        return config
    except Exception as e:
        print(f"[오류] 설정 파일을 읽는 중 문제가 발생했습니다: {e}")
        return get_default_config()

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"[오류] 설정 파일을 저장하는 중 문제가 발생했습니다: {e}")
        return False