import os

SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')

def load_projects(folder_path, sort_method="modified"):
    """
    지정된 폴더 경로에서 하위 폴더(작품) 이름만 추출하여 리스트로 반환합니다.
    """
    if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return []
    
    projects = []
    try:
        for item in os.listdir(folder_path):
            if item.startswith('.'):
                continue
                
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                projects.append(item)
    except Exception as e:
        print(f"[오류] 폴더를 읽는 중 문제가 발생했습니다: {e}")
        return []
    
    if sort_method == "modified":
        projects.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
    else:
        projects.sort()
        
    return projects

def load_images(project_path):
    """지정된 작품 폴더에서 지원하는 이미지 파일명만 추출하여 숫자 기준으로 정렬해 반환합니다."""
    if not project_path or not os.path.exists(project_path) or not os.path.isdir(project_path):
        return []
        
    image_files = []
    try:
        for item in os.listdir(project_path):
            if item.lower().endswith(SUPPORTED_EXTENSIONS):
                item_path = os.path.join(project_path, item)
                if os.path.isfile(item_path):
                    image_files.append(item)
    except Exception as e:
        print(f"[오류] 이미지 폴더를 읽는 중 문제가 발생했습니다: {e}")
        return []

    def sort_key(filename):
        base_name = os.path.splitext(filename)[0]
        try:
            parts = base_name.split('_')
            return (int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            return (float('inf'), float('inf'), filename)

    return sorted(image_files, key=sort_key)