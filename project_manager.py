import os
import shutil
import datetime
import platform
import subprocess
import json

def project_exists(base_folder, project_name):
    if not base_folder or not project_name:
        return False
    path = os.path.join(base_folder, project_name)
    return os.path.exists(path) and os.path.isdir(path)

def create_project(base_folder, project_name):
    path = os.path.join(base_folder, project_name)
    os.makedirs(path, exist_ok=True)
    return path

def copy_images(project_path, image_paths):
    for file_path in image_paths:
        try:
            shutil.copy2(file_path, project_path)
        except Exception as e:
            print(f"[오류] 파일 복사 실패 ({file_path}): {e}")

def analyze_import_files(file_paths):
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
        start_turn = prev_turn = turns[0]
        count_in_range = turn_counts[start_turn]
        for t in turns[1:]:
            if t == prev_turn + 1:
                prev_turn = t
                count_in_range += turn_counts[t]
            else:
                turn_ranges.append({"start": start_turn, "end": prev_turn, "count": count_in_range})
                start_turn = prev_turn = t
                count_in_range = turn_counts[t]
        turn_ranges.append({"start": start_turn, "end": prev_turn, "count": count_in_range})
    return {"valid_files": valid_files, "invalid_files": invalid_files, "turns": turns, "turn_counts": turn_counts, "turn_ranges": turn_ranges}

def get_project_summary(project_path):
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
    return {"image_count": image_count, "turn_count": len(turns), "last_modified": dt.strftime("%Y-%m-%d")}

def open_project_folder(project_path):
    if not os.path.exists(project_path):
        return False
    system = platform.system()
    try:
        if system == "Windows": os.startfile(project_path)
        elif system == "Darwin": subprocess.call(["open", project_path])
        else: subprocess.call(["xdg-open", project_path])
        return True
    except:
        return False

def rename_project(base_folder, old_name, new_name):
    old_path = os.path.join(base_folder, old_name)
    new_path = os.path.join(base_folder, new_name)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        try:
            os.rename(old_path, new_path)
            return True
        except:
            return False
    return False

# ==========================================
# 휴지통 및 메타데이터 처리 (v1.9.1 개선)
# ==========================================
def move_to_trash(base_folder, project_name):
    project_path = os.path.join(base_folder, project_name)
    if not os.path.exists(project_path):
        return False

    # v1.9.1: 이동 전 요약 정보를 미리 가져옴
    info = get_project_summary(project_path)
    
    trash_dir = os.path.join(base_folder, ".Trash")
    os.makedirs(trash_dir, exist_ok=True)

    trashed_name = project_name
    trash_project_path = os.path.join(trash_dir, trashed_name)
    
    if os.path.exists(trash_project_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        trashed_name = f"{project_name}_{timestamp}"
        trash_project_path = os.path.join(trash_dir, trashed_name)

    meta_path = os.path.join(trash_dir, f"{trashed_name}.meta.json")

    try:
        shutil.move(project_path, trash_project_path)
        
        # v1.9.1: 추가 메타데이터 저장
        meta_data = {
            "original_name": project_name,
            "trashed_name": trashed_name,
            "deleted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "turn_count": info["turn_count"],
            "image_count": info["image_count"],
            "last_modified": info["last_modified"]
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"[오류] 휴지통 이동 실패: {e}")
        return False

def get_trashed_projects(base_folder):
    trash_dir = os.path.join(base_folder, ".Trash")
    if not os.path.exists(trash_dir):
        return []

    trashed_list = []
    for item in os.listdir(trash_dir):
        if item.endswith(".meta.json"):
            meta_path = os.path.join(trash_dir, item)
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    trashed_list.append(data)
            except:
                pass
    return sorted(trashed_list, key=lambda x: x.get("deleted_at", ""), reverse=True)

def restore_from_trash(base_folder, trashed_name, original_name):
    trash_dir = os.path.join(base_folder, ".Trash")
    trash_project_path = os.path.join(trash_dir, trashed_name)
    meta_path = os.path.join(trash_dir, f"{trashed_name}.meta.json")
    restore_path = os.path.join(base_folder, original_name)
    
    if os.path.exists(restore_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        restore_path = os.path.join(base_folder, f"{original_name}_복원_{timestamp}")

    try:
        shutil.move(trash_project_path, restore_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
        return True
    except Exception as e:
        print(f"[오류] 복원 실패: {e}")
        return False

def permanent_delete(base_folder, trashed_name):
    trash_dir = os.path.join(base_folder, ".Trash")
    trash_project_path = os.path.join(trash_dir, trashed_name)
    meta_path = os.path.join(trash_dir, f"{trashed_name}.meta.json")

    try:
        if os.path.exists(trash_project_path):
            shutil.rmtree(trash_project_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
        return True
    except Exception as e:
        print(f"[오류] 영구 삭제 실패: {e}")
        return False

def empty_trash(base_folder):
    trash_dir = os.path.join(base_folder, ".Trash")
    if os.path.exists(trash_dir):
        try:
            shutil.rmtree(trash_dir)
            return True
        except Exception as e:
            print(f"[오류] 휴지통 비우기 실패: {e}")
            return False
    return True