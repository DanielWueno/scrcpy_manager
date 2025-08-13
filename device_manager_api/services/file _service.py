import json
import os
from typing import List, Dict, Any

class FileService:
    @staticmethod
    def save_json(data: List[Dict], file_path: str) -> bool:
        """Guarda datos en archivo JSON"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando archivo: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> List[Dict]:
        """Carga datos desde archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error cargando archivo: {e}")
            return []
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> None:
        """Crea directorio si no existe"""
        os.makedirs(directory, exist_ok=True)