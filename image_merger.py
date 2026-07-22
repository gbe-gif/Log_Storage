import os
from PIL import Image

def merge_images(project_path, image_list):
    """
    이미지 파일명 리스트를 첫 번째 숫자(turn) 기준으로 그룹화하고,
    같은 그룹의 이미지들을 세로로 병합하여 반환합니다.
    """
    groups = {}
    
    for filename in image_list:
        try:
            base_name = os.path.splitext(filename)[0]
            turn = int(base_name.split('_')[0])
            
            if turn not in groups:
                groups[turn] = []
            groups[turn].append(filename)
        except (ValueError, IndexError):
            print(f"[경고] 파일명 파싱 실패 (병합 제외): {filename}")
            continue

    result = []
    
    for turn in sorted(groups.keys()):
        files = groups[turn]
        images = []
        
        for file in files:
            img_path = os.path.join(project_path, file)
            try:
                # with 구문을 사용하여 파일 핸들러 안전하게 닫기
                with Image.open(img_path) as img:
                    # RGBA로 변환한 이미지만 메모리에 보관
                    images.append(img.convert("RGBA"))
            except Exception as e:
                print(f"[오류] 이미지 열기 실패 ({img_path}): {e}")
        
        if not images:
            continue
            
        if len(images) == 1:
            merged_image = images[0]
        else:
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)
            
            merged_image = Image.new('RGBA', (max_width, total_height))
            
            y_offset = 0
            for img in images:
                merged_image.paste(img, (0, y_offset), img)
                y_offset += img.height
                
        # 반환 구조 확장 (turn, files, image)
        result.append({
            "turn": turn,
            "files": files,
            "image": merged_image
        })
        
    return result