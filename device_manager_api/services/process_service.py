import subprocess
import platform
import psutil
from typing import Dict, List, Optional

class ProcessService:
    @staticmethod
    def is_windows() -> bool:
        return platform.system() == "Windows"
    
    @staticmethod
    def run_command(command: List[str], timeout: int = 30) -> Dict:
        """Ejecuta comando y retorna resultado"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Comando expiró'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def find_processes_by_name(name: str) -> List[Dict]:
        """Encuentra procesos por nombre"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if name.lower() in proc.info['name'].lower():
                    processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes