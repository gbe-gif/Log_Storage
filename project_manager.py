import os
import shutil
import datetime
import platform
import subprocess

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
    """파일 경로 리스트를 분석하여 정상/비정상 파일을 분류하고 Turn 통계를 계산합니다."""
    valid_files = []
    invalid_files = []
    turn_counts = {}

    for file_path in file_paths:
        basename = os.path.basename(file_path)
        name_no_ext, ext = os.path.splitext(basename)
        parts = name_no_ext.split('_')
        
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            turn = int(parts[0])
            valid_files.append(file_path)
            turn_counts[turn] = turn_counts.get(turn, 0) + 1
        else:
            invalid_files.append(basename)

    turns = sorted(list(turn_counts.keys()))
    turn_ranges = []

    if turns:
        start_turn = turns[0]
        prev_turn = turns[0]
        count_in_range = turn_counts[start_turn]

        for t in turns[1:]:
            if t == prev_turn + 1:
                prev_turn = t
                count_in_range += turn_counts[t]
            else:
                turn_ranges.append({"start": start_turn, "end": prev_turn, "count": count_in_range})
                start_turn = t
                prev_turn = t
                count_in_range = turn_counts[t]
        
        turn_ranges.append({"start": start_turn, "end": prev_turn, "count": count_in_range})

    return {
        "valid_files": valid_files,
        "invalid_files": invalid_files,
        "turns": turns,
        "turn_counts": turn_counts,
        "turn_ranges": turn_ranges
    }

def get_project_summary(project_path):
    """해당 프로젝트의 현재 상태(이미지 수, Turn 수, 마지막 수정일)를 분석하여 반환합니다."""
    if not os.path.exists(project_path):
        return {"image_count": 0, "turn_count": 0, "last_modified": "-"}
        
    image_count = 0
    turns = set()
    max_mtime = os.path.getmtime(project_path)
    
    try:
        files = os.listdir(project_path)
        for f in files:
            if f.lower().endswith('.png'):
                filepath = os.path.join(project_path, f)
                if os.path.isfile(filepath):
                    name_no_ext = os.path.splitext(f)[0]
                    parts = name_no_ext.split('_')
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        image_count += 1
                        turns.add(int(parts[0]))
                        
                        mtime = os.path.getmtime(filepath)
                        if mtime > max_mtime:
                            max_mtime = mtime
    except Exception:
        pass
        
    dt = datetime.datetime.fromtimestamp(max_mtime)
    return {
        "image_count": image_count,
        "turn_count": len(turns),
        "last_modified": dt.strftime("%Y-%m-%d")
    }

# ==========================================
# v1.6 추가: 프로젝트 관리 기능
# ==========================================

def open_project_folder(project_path):
    """운영체제의 기본 파일 탐색기로 프로젝트 폴더를 엽니다."""
    if not os.path.exists(project_path):
        return
        
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(project_path)
        elif system == "Darwin":
            subprocess.call(["open", project_path])
        else:
            subprocess.call(["xdg-open", project_path])
    except Exception as e:
        print(f"[오류] 폴더 열기 실패 ({project_path}): {e}")

def rename_project(base_folder, old_name, new_name):
    """프로젝트 폴더의 이름을 변경합니다."""
    old_path = os.path.join(base_folder, old_name)
    new_path = os.path.join(base_folder, new_name)
    
    if os.path.exists(old_path) and not os.path.exists(new_path):
        try:
            os.rename(old_path, new_path)
            return True
        except Exception as e:
            print(f"[오류] 이름 변경 실패: {e}")
            return False
    return False

def delete_project(project_path):
    """프로젝트 폴더와 그 안의 모든 데이터를 삭제합니다."""
    if os.path.exists(project_path):
        try:
            shutil.rmtree(project_path)
            return True
        except Exception as e:
            print(f"[오류] 폴더 삭제 실패: {e}")
            return False
    return False