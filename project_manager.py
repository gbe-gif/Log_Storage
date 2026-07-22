import os
import shutil

def project_exists(base_folder, project_name):
    """지정된 저장소에 해당 이름의 작품(폴더)이 이미 존재하는지 확인합니다."""
    if not base_folder or not project_name:
        return False
    path = os.path.join(base_folder, project_name)
    return os.path.exists(path) and os.path.isdir(path)

def create_project(base_folder, project_name):
    """새로운 작품 폴더를 생성하고 그 경로를 반환합니다."""
    path = os.path.join(base_folder, project_name)
    os.makedirs(path, exist_ok=True)
    return path

def copy_images(project_path, image_paths):
    """선택된 유효한 이미지 파일들을 프로젝트 폴더로 복사합니다."""
    for file_path in image_paths:
        try:
            shutil.copy2(file_path, project_path)
        except Exception as e:
            print(f"[오류] 파일 복사 실패 ({file_path}): {e}")

def analyze_import_files(file_paths):
    """
    파일 경로 리스트를 분석하여 정상/비정상 파일을 분류하고 Turn 통계를 계산합니다.
    정상 파일 포맷: 정수_정수.png
    """
    valid_files = []
    invalid_files = []
    turn_counts = {}

    for file_path in file_paths:
        basename = os.path.basename(file_path)
        name_no_ext, ext = os.path.splitext(basename)

        parts = name_no_ext.split('_')
        
        # 정확히 '_'로 2등분되며, 둘 다 숫자로 이루어져 있는지 엄격히 검사
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            turn = int(parts[0])
            valid_files.append(file_path)
            turn_counts[turn] = turn_counts.get(turn, 0) + 1
        else:
            invalid_files.append(basename)

    turns = sorted(list(turn_counts.keys()))
    turn_ranges = []

    # 연속된 Turn 번호를 하나의 구간으로 묶어 통계 생성
    if turns:
        start_turn = turns[0]
        prev_turn = turns[0]
        count_in_range = turn_counts[start_turn]

        for t in turns[1:]:
            if t == prev_turn + 1:
                # 연속된 Turn이면 묶음
                prev_turn = t
                count_in_range += turn_counts[t]
            else:
                # 연속이 끊어지면 이전 구간을 저장하고 새로 시작
                turn_ranges.append({
                    "start": start_turn,
                    "end": prev_turn,
                    "count": count_in_range
                })
                start_turn = t
                prev_turn = t
                count_in_range = turn_counts[t]
        
        # 마지막 구간 저장
        turn_ranges.append({
            "start": start_turn,
            "end": prev_turn,
            "count": count_in_range
        })

    return {
        "valid_files": valid_files,
        "invalid_files": invalid_files,
        "turns": turns,
        "turn_counts": turn_counts,
        "turn_ranges": turn_ranges
    }