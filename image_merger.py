import os
from PIL import Image

def merge_images(project_path, image_list):
    """
    이미지 파일명 리스트를 첫 번째 숫자(turn) 기준으로 그룹화하고,
    같은 그룹의 이미지들을 세로로 병합하여 반환합니다.
    
    반환 형식:
    [
        {"turn": 1, "image": PIL.Image},
        {"turn": 2, "image": PIL.Image},
        ...
    ]
    """
    groups = {}
    
    # 1. 파일명을 첫 번째 숫자 기준으로 그룹화
    for filename in image_list:
        try:
            # "1_1.png" -> 확장자 제거 후 "_"로 분할하여 첫 번째 요소를 int로 변환
            base_name = os.path.splitext(filename)[0]
            turn = int(base_name.split('_')[0])
            
            if turn not in groups:
                groups[turn] = []
            groups[turn].append(filename)
        except (ValueError, IndexError):
            print(f"[경고] 파일명 파싱 실패 (병합 제외): {filename}")
            continue

    result = []
    
    # turn 번호순으로 정렬하여 처리 (image_list가 전달된 순서는 그룹 내에서 유지됨)
    for turn in sorted(groups.keys()):
        files = groups[turn]
        images = []
        
        for file in files:
            img_path = os.path.join(project_path, file)
            try:
                img = Image.open(img_path)
                # 이미지를 메모리에 강제로 로드하여 이후 원본 파일이 닫히거나 변경되어도 문제없게 처리
                img.load()
                # PNG 포맷의 투명도를 일관되게 다루기 위해 RGBA로 변환
                img = img.convert("RGBA") 
                images.append(img)
            except Exception as e:
                print(f"[오류] 이미지 열기 실패 ({img_path}): {e}")
        
        if not images:
            continue
            
        # 3. 그룹에 이미지가 하나뿐이면 병합하지 않고 그대로 사용
        if len(images) == 1:
            merged_image = images[0]
        else:
            # 2. 같은 그룹의 이미지를 세로 방향으로 이어붙임
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)
            
            # 새로운 투명 배경의 도화지 생성
            merged_image = Image.new('RGBA', (max_width, total_height))
            
            y_offset = 0
            for img in images:
                # 붙여넣을 때 투명도 마스크(img 자체)를 적용하여 알파 채널 보존
                merged_image.paste(img, (0, y_offset), img)
                y_offset += img.height
                
        # 4. PIL.Image 객체를 포함한 딕셔너리 형태로 반환 결과 추가
        result.append({
            "turn": turn,
            "image": merged_image
        })
        
    return result