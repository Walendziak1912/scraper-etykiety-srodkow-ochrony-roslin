import json, shutil
from pathlib import Path
from typing import Union, Optional
from pathlib import Path

def get_screenshots_dir(path: Optional[Union[str, Path]] = None) -> Path:
    screenshots_path = Path(path)
    screenshots_path.mkdir(parents=True, exist_ok=True)
    return screenshots_path

def read_file_to_bytes(
    filename: Union[str, Path],
    base_dir: Optional[Union[str, Path]] = None
) -> bytes:
    filename_path = Path(filename)
    
    if filename_path.is_absolute() or '..' in str(filename_path):
        file_path = filename_path
        
    elif base_dir is not None:
        base_dir_path = Path(base_dir)
        file_path = base_dir_path / filename_path.name
    else:
        file_path = filename_path
    return file_path.read_bytes()


def save_bytes_to_file(
    data: bytes,
    filename: Union[str, Path],
    base_dir: Optional[Union[str, Path]] = None
) -> Path:
    filename_path = Path(filename)
    
    if filename_path.is_absolute() or '..' in str(filename_path):
        file_path = filename_path
    elif base_dir is not None:
        base_dir_path = Path(base_dir)
        file_path = base_dir_path / filename_path.name
    else:
        file_path = filename_path

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(data)

    return file_path

def clear_dir(path_dir: Path) -> None:
    try:
        deleted_count = 0
        for item in path_dir.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                deleted_count += 1
            except Exception as e:
                print(f'Błąd podczas usuwania {item}: {e}')
    except Exception as e:
        pass
    finally:
        print(f'Katalog {path_dir} został wyczyszczony.')
        
def save_result_to_jsonlines(result: dict, result_path: Union[str, Path]) -> None:
    result_path = Path(result_path)
    result_path.parent.mkdir(parents=True, exist_ok=True)

    with result_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
        
    
