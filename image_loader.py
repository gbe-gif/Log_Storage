import os

def load_projects(folder_path):
    """
    지정된 폴더 경로에서 하위 폴더(작품) 이름만 추출하여 정렬된 리스트로 반환합니다.
    파일은 무시하며, 유효하지 않은 경로일 경우 빈 리스트를 반환합니다.
    """
    if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return []
    
    projects = []
    try:
        # 폴더 내 항목 탐색
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # 디렉토리인 경우에만 추가 (파일 무시)
            if os.path.isdir(item_path):
                projects.append(item)
    except Exception as e:
        print(f"[오류] 폴더를 읽는 중 문제가 발생했습니다: {e}")
        return []
    
    # 이름순으로 정렬하여 반환
    return sorted(projects)