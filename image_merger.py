import os
from PIL import Image

def merge_images(project_path, image_files):
    """
    동일한 Turn에 속하는 이미지들을 세로로 병합하여 리스트로 반환합니다.
    확장자가 달라도 Turn 번호가 같으면 함께 묶입니다.
    """
    if not image_files:
        return []

    turn_groups = {}

    # 1. Turn별로 파일 그룹화
    for filename in image_files:
        name_no_ext, _ = os.path.splitext(filename)
        parts = name_no_ext.split('_')
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            turn_num = int(parts[0])
            if turn_num not in turn_groups:
                turn_groups[turn_num] = []
            turn_groups[turn_num].append(filename)

    merged_results = []

    # 2. 각 Turn별 이미지들을 세로로 병합
    for turn_num in sorted(turn_groups.keys()):
        # 파일명을 내부 정렬 규칙(순번 기준)에 따라 정렬
        files_in_turn = sorted(turn_groups[turn_num], key=lambda f: int(os.path.splitext(f)[0].split('_')[1]))
        
        pil_images = []
        valid_filenames = []

        for filename in files_in_turn:
            filepath = os.path.join(project_path, filename)
            try:
                img = Image.open(filepath)
                # RGBA나 팔레트 모드 등을 RGB/RGBA로 안전하게 변환
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGBA')
                pil_images.append(img)
                valid_filenames.append(filename)
            except Exception as e:
                print(f"[오류] 이미지 파일을 여는 중 문제가 발생했습니다 ({filename}): {e}")

        if not pil_images:
            continue

        # 세로 병합 수행
        total_width = max(img.width for img in pil_images)
        total_height = sum(img.height for img in pil_images)

        # 투명도를 지원하는 RGBA 모드로 새 캔버스 생성
        merged_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
        
        y_offset = 0
        for img in pil_images:
            # 가로 폭이 다를 경우 가운데 정렬 또는 좌측 정렬 (여기서는 좌측/너비 맞춤)
            merged_img.paste(img, (0, y_offset))
            y_offset += img.height

        merged_results.append({
            "turn": turn_num,
            "files": valid_filenames,
            "image": merged_img
        })

    return merged_results