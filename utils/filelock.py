"""
Cross-platform file locking utility for safe concurrent writes.
"""

import os
import time
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Union

try:
    import fcntl  # Unix/Linux
    FCNTL_AVAILABLE = True
except ImportError:
    FCNTL_AVAILABLE = False

try:
    import msvcrt  # Windows
    MSVCRT_AVAILABLE = True
except ImportError:
    MSVCRT_AVAILABLE = False


class FileLockError(Exception):
    """Raised when file locking operations fail."""
    pass


class FileLock:
    """Cross-platform file lock implementation."""
    
    def __init__(self, file_path: Union[str, Path], timeout: float = 10.0):
        self.file_path = Path(file_path)
        self.timeout = timeout
        self.lock_file_path = self.file_path.with_suffix(self.file_path.suffix + '.lock')
        self.lock_fd = None
        self.acquired = False
    
    def acquire(self) -> bool:
        """Acquire the file lock."""
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            try:
                # Create lock file
                self.lock_fd = open(self.lock_file_path, 'w')
                
                if FCNTL_AVAILABLE:
                    # Unix/Linux: use fcntl
                    fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                elif MSVCRT_AVAILABLE:
                    # Windows: use msvcrt
                    msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    # Fallback: use lock file existence (not atomic, but works)
                    if self.lock_file_path.exists():
                        self.lock_fd.close()
                        raise FileLockError("Lock file exists")
                
                # Write lock info
                self.lock_fd.write(f"pid:{os.getpid()}\ntime:{datetime.now().isoformat()}\n")
                self.lock_fd.flush()
                self.acquired = True
                return True
                
            except (OSError, IOError, FileLockError):
                if self.lock_fd:
                    self.lock_fd.close()
                    self.lock_fd = None
                time.sleep(0.1)  # Wait 100ms before retry
        
        return False
    
    def release(self):
        """Release the file lock."""
        if not self.acquired or not self.lock_fd:
            return
        
        try:
            if FCNTL_AVAILABLE:
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
            elif MSVCRT_AVAILABLE:
                msvcrt.locking(self.lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
            
            self.lock_fd.close()
            self.lock_fd = None
            
            # Remove lock file
            if self.lock_file_path.exists():
                self.lock_file_path.unlink()
                
        except (OSError, IOError):
            pass  # Best effort cleanup
        
        self.acquired = False
    
    def __enter__(self):
        if not self.acquire():
            raise FileLockError(f"Could not acquire lock for {self.file_path} within {self.timeout}s")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


@contextmanager
def locked_file_write(file_path: Union[str, Path], timeout: float = 10.0):
    """
    Context manager for safe file writes with locking and backup.
    
    Args:
        file_path: Path to the file to write
        timeout: Timeout in seconds for acquiring the lock
        
    Yields:
        Path object for the file to write to
        
    Example:
        with locked_file_write("data.csv") as f:
            df.to_csv(f, index=False)
    """
    file_path = Path(file_path)
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create backup if file exists
    backup_path = None
    if file_path.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = file_path.parent.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        
        # Copy to backup
        import shutil
        shutil.copy2(file_path, backup_path)
    
    # Acquire lock and write
    with FileLock(file_path, timeout=timeout):
        try:
            yield file_path
        except Exception:
            # If write failed and we have a backup, restore it
            if backup_path and backup_path.exists():
                import shutil
                shutil.copy2(backup_path, file_path)
            raise


def cleanup_old_backups(backup_dir: Union[str, Path], file_pattern: str, keep_days: int = 7):
    """
    Clean up old backup files.
    
    Args:
        backup_dir: Directory containing backups
        file_pattern: Pattern to match backup files (e.g., "acquisitions_*.csv")
        keep_days: Number of days of backups to keep
    """
    backup_dir = Path(backup_dir)
    if not backup_dir.exists():
        return
    
    cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
    
    for backup_file in backup_dir.glob(file_pattern):
        if backup_file.stat().st_mtime < cutoff_time:
            try:
                backup_file.unlink()
            except OSError:
                pass  # Best effort cleanup