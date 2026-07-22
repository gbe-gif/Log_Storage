import os
import json

CONFIG_FILE = "config.json"

def get_default_config():
    """기본 설정값을 반환합니다."""
    return {
        "storage_root": os.path.dirname(os.path.abspath(__file__)),
        "theme": "dark"
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
            
            # v1.8: 누락된 키가 있으면 기본값으로 채움
            default_config = get_default_config()
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
                    
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