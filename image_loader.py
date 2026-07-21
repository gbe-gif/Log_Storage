import os

def load_projects(folder_path):
    """
    지정된 폴더 경로에서 하위 폴더(작품) 이름만 추출하여 정렬된 리스트로 반환합니다.
    """
    if not folder_path or not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return []
    
    projects = []
    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                projects.append(item)
    except Exception as e:
        print(f"[오류] 폴더를 읽는 중 문제가 발생했습니다: {e}")
        return []
    
    return sorted(projects)

def load_images(project_path):
    """
    지정된 작품 폴더에서 PNG 이미지 파일명만 추출하여 리스트로 반환합니다.
    파일명 형식이 'X_Y.png' 인 경우를 상정하여 숫자 기준으로 정렬합니다.
    """
    if not project_path or not os.path.exists(project_path) or not os.path.isdir(project_path):
        return []
        
    png_files = []
    try:
        for item in os.listdir(project_path):
            # 대소문자 구분 없이 png 확장자 확인
            if item.lower().endswith('.png'):
                item_path = os.path.join(project_path, item)
                # 하위 폴더는 무시하고 파일만 추가
                if os.path.isfile(item_path):
                    png_files.append(item)
    except Exception as e:
        print(f"[오류] 이미지 폴더를 읽는 중 문제가 발생했습니다: {e}")
        return []

    # 숫자 기준 정렬용 키 함수
    def sort_key(filename):
        # 확장자 분리 ("10_1.png" -> "10_1")
        base_name = os.path.splitext(filename)[0]
        try:
            # "_"를 기준으로 분리하여 정수형으로 변환
            parts = base_name.split('_')
            first_num = int(parts[0])
            second_num = int(parts[1])
            return (first_num, second_num)
        except (ValueError, IndexError):
            # 파일명이 숫자_숫자 패턴이 아닌 경우 맨 뒤로 보내기 위한 예외 처리
            return (float('inf'), float('inf'), filename)

    # 문자열 정렬이 아닌 반환된 튜플(숫자) 기준으로 정렬
    return sorted(png_files, key=sort_key)