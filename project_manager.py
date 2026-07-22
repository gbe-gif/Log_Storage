import os
import shutil
import datetime
import platform
import subprocess
import json

# (기존 유틸리티 함수 및 휴지통 관련 함수들은 이전 버전과 완전히 동일하게 유지합니다. 생략 없이 전체를 복사/붙여넣기 하시면 됩니다.)

def project_exists(base_folder, project_name):
    if not base_folder or not project_name: return False
    return os.path.exists(os.path.join(base_folder, project_name)) and os.path.isdir(os.path.join(base_folder, project_name))

def create_project(base_folder, project_name):
    path = os.path.join(base_folder, project_name)
    os.makedirs(path, exist_ok=True)
    return path

def copy_images(project_path, image_paths):
    for file_path in image_paths:
        try: shutil.copy2(file_path, project_path)
        except Exception as e: print(f"[오류] 파일 복사 실패 ({file_path}): {e}")

def analyze_import_files(file_paths):
    valid_files, invalid_files, turn_counts = [], [], {}
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
    image_count, turns = 0, set()
    max_mtime = os.path.getmtime(project_path)
    try:
        for f in os.listdir(project_path):
            if f.lower().endswith('.png'):
                filepath = os.path.join(project_path, f)
                if os.path.isfile(filepath):
                    parts = os.path.splitext(f)[0].split('_')
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        image_count += 1
                        turns.add(int(parts[0]))
                        mtime = os.path.getmtime(filepath)
                        if mtime > max_mtime: max_mtime = mtime
    except Exception: pass
    dt = datetime.datetime.fromtimestamp(max_mtime)
    return {"image_count": image_count, "turn_count": len(turns), "last_modified": dt.strftime("%Y-%m-%d")}

def open_project_folder(project_path):
    if not os.path.exists(project_path): return False
    system = platform.system()
    try:
        if system == "Windows": os.startfile(project_path)
        elif system == "Darwin": subprocess.call(["open", project_path])
        else: subprocess.call(["xdg-open", project_path])
        return True
    except: return False

def rename_project(base_folder, old_name, new_name):
    old_path = os.path.join(base_folder, old_name)
    new_path = os.path.join(base_folder, new_name)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        try:
            os.rename(old_path, new_path)
            return True
        except: return False
    return False

def move_to_trash(base_folder, project_name):
    project_path = os.path.join(base_folder, project_name)
    if not os.path.exists(project_path): return False
    info = get_project_summary(project_path)
    trash_dir = os.path.join(base_folder, ".Trash")
    os.makedirs(trash_dir, exist_ok=True)
    trashed_name = project_name
    trash_project_path = os.path.join(trash_dir, trashed_name)
    if os.path.exists(trash_project_path):
        trashed_name = f"{project_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        trash_project_path = os.path.join(trash_dir, trashed_name)
    meta_path = os.path.join(trash_dir, f"{trashed_name}.meta.json")
    try:
        shutil.move(project_path, trash_project_path)
        meta_data = {
            "original_name": project_name, "trashed_name": trashed_name,
            "deleted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "turn_count": info["turn_count"], "image_count": info["image_count"],
            "last_modified": info["last_modified"]
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=4)
        return True
    except: return False

def get_trashed_projects(base_folder):
    trash_dir = os.path.join(base_folder, ".Trash")
    if not os.path.exists(trash_dir): return []
    trashed_list = []
    for item in os.listdir(trash_dir):
        if item.endswith(".meta.json"):
            try:
                with open(os.path.join(trash_dir, item), "r", encoding="utf-8") as f:
                    trashed_list.append(json.load(f))
            except: pass
    return sorted(trashed_list, key=lambda x: x.get("deleted_at", ""), reverse=True)

def restore_from_trash(base_folder, trashed_name, original_name):
    trash_dir = os.path.join(base_folder, ".Trash")
    trash_project_path = os.path.join(trash_dir, trashed_name)
    meta_path = os.path.join(trash_dir, f"{trashed_name}.meta.json")
    restore_path = os.path.join(base_folder, original_name)
    if os.path.exists(restore_path):
        restore_path = os.path.join(base_folder, f"{original_name}_복원_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
    try:
        shutil.move(trash_project_path, restore_path)
        if os.path.exists(meta_path): os.remove(meta_path)
        return True
    except: return False

def permanent_delete(base_folder, trashed_name):
    trash_dir = os.path.join(base_folder, ".Trash")
    trash_project_path = os.path.join(trash_dir, trashed_name)
    meta_path = os.path.join(trash_dir, f"{trashed_name}.meta.json")
    try:
        if os.path.exists(trash_project_path): shutil.rmtree(trash_project_path)
        if os.path.exists(meta_path): os.remove(meta_path)
        return True
    except: return False

def empty_trash(base_folder):
    trash_dir = os.path.join(base_folder, ".Trash")
    if os.path.exists(trash_dir):
        try:
            shutil.rmtree(trash_dir)
            return True
        except: return False
    return True

def get_project_meta(project_path):
    """프로젝트 폴더 내의 메타데이터를 읽어 반환합니다."""
    meta_path = os.path.join(project_path, ".project_meta.json")
    # v2.0 개선: turn_aliases 추가
    default_meta = {"favorite": False, "bookmarks": {}, "turn_aliases": {}}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**default_meta, **data}
        except: pass
    return default_meta

def save_project_meta(project_path, meta):
    """프로젝트 폴더 내에 메타데이터를 저장합니다."""
    meta_path = os.path.join(project_path, ".project_meta.json")
    try:
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

def get_cover_path(base_folder):
    if not base_folder: return None
    for ext in ['.png', '.jpg', '.jpeg', '.webp']:
        p = os.path.join(base_folder, f"cover{ext}")
        if os.path.exists(p): return p
    return None

def set_cover_image(base_folder, source_path):
    if not base_folder or not source_path: return False
    delete_cover_image(base_folder)
    
    ext = os.path.splitext(source_path)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg', '.webp']: ext = '.png'
    dest = os.path.join(base_folder, f"cover{ext}")
    try:
        shutil.copy2(source_path, dest)
        return True
    except: return False

def delete_cover_image(base_folder):
    if not base_folder: return False
    deleted = False
    for ext in ['.png', '.jpg', '.jpeg', '.webp']:
        p = os.path.join(base_folder, f"cover{ext}")
        if os.path.exists(p):
            os.remove(p)
            deleted = True
    return deleted