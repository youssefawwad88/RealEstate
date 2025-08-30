"""
Test file locking functionality.
"""

import pytest
import pandas as pd
import tempfile
import time
import threading
from pathlib import Path
from unittest.mock import patch

from utils.filelock import FileLock, FileLockError, locked_file_write, cleanup_old_backups


class TestFileLock:
    """Test file locking functionality."""
    
    def test_file_lock_basic(self):
        """Test basic file lock acquire and release."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.csv"
            
            lock = FileLock(test_file)
            assert lock.acquire()
            assert lock.acquired
            
            lock.release()
            assert not lock.acquired
    
    def test_file_lock_context_manager(self):
        """Test file lock as context manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.csv"
            
            with FileLock(test_file) as lock:
                assert lock.acquired
            
            assert not lock.acquired
    
    def test_file_lock_timeout(self):
        """Test file lock timeout behavior."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.csv"
            
            # Acquire lock first
            lock1 = FileLock(test_file, timeout=0.5)
            assert lock1.acquire()
            
            try:
                # Second lock should timeout
                lock2 = FileLock(test_file, timeout=0.5)
                assert not lock2.acquire()
                
                # Context manager should raise error
                with pytest.raises(FileLockError, match="Could not acquire lock"):
                    with FileLock(test_file, timeout=0.5):
                        pass
                        
            finally:
                lock1.release()
    
    def test_locked_file_write_basic(self):
        """Test basic locked file write functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.csv"
            
            # Write some data
            test_data = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
            
            with locked_file_write(test_file) as file_path:
                test_data.to_csv(file_path, index=False)
            
            # Verify file was written
            assert test_file.exists()
            written_data = pd.read_csv(test_file)
            pd.testing.assert_frame_equal(written_data, test_data)
    
    def test_locked_file_write_with_backup(self):
        """Test that backups are created during locked writes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "data" / "processed" / "test.csv"
            backup_dir = temp_path / "data" / "backups"
            
            # Create initial file
            test_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = pd.DataFrame({'col1': [1], 'col2': ['initial']})
            initial_data.to_csv(test_file, index=False)
            
            # Update file with locked write
            updated_data = pd.DataFrame({'col1': [1, 2], 'col2': ['initial', 'updated']})
            
            with locked_file_write(test_file) as file_path:
                updated_data.to_csv(file_path, index=False)
            
            # Verify file was updated
            final_data = pd.read_csv(test_file)
            pd.testing.assert_frame_equal(final_data, updated_data)
            
            # Verify backup was created
            assert backup_dir.exists()
            backup_files = list(backup_dir.glob("test_*.csv"))
            assert len(backup_files) >= 1
            
            # Verify backup contains original data
            backup_data = pd.read_csv(backup_files[0])
            pd.testing.assert_frame_equal(backup_data, initial_data)
    
    def test_concurrent_writes_simulation(self):
        """Test that concurrent writes work correctly with locking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "concurrent_test.csv"
            
            # Create initial file
            initial_data = pd.DataFrame({'id': [], 'value': []})
            initial_data.to_csv(test_file, index=False)
            
            results = []
            errors = []
            
            def write_worker(worker_id, start_id):
                """Worker function to simulate concurrent writes."""
                try:
                    # Load existing data, add new row, save back
                    with locked_file_write(test_file, timeout=5.0) as file_path:
                        if file_path.exists():
                            existing_df = pd.read_csv(file_path)
                        else:
                            existing_df = pd.DataFrame({'id': [], 'value': []})
                        
                        # Add new row
                        new_row = pd.DataFrame({'id': [start_id + worker_id], 'value': [f'worker_{worker_id}']})
                        combined_df = pd.concat([existing_df, new_row], ignore_index=True)
                        
                        # Small delay to increase chance of conflicts
                        time.sleep(0.01)
                        
                        # Write back
                        combined_df.to_csv(file_path, index=False)
                        results.append(worker_id)
                        
                except Exception as e:
                    errors.append((worker_id, str(e)))
            
            # Start multiple workers
            threads = []
            num_workers = 5
            for i in range(num_workers):
                thread = threading.Thread(target=write_worker, args=(i, 100))
                threads.append(thread)
                thread.start()
            
            # Wait for all to complete
            for thread in threads:
                thread.join()
            
            # Check results
            assert len(errors) == 0, f"Errors occurred: {errors}"
            assert len(results) == num_workers
            
            # Verify final file is valid and contains all data
            final_data = pd.read_csv(test_file)
            assert len(final_data) == num_workers
            
            # All IDs should be unique and in expected range
            ids = sorted(final_data['id'].tolist())
            expected_ids = sorted([100 + i for i in range(num_workers)])
            assert ids == expected_ids
    
    def test_backup_creation_and_cleanup(self):
        """Test backup creation and cleanup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "data" / "processed" / "test.csv"
            backup_dir = temp_path / "data" / "backups"
            
            # Create initial file
            test_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = pd.DataFrame({'col1': [1], 'col2': ['test']})
            initial_data.to_csv(test_file, index=False)
            
            # Perform multiple writes to create multiple backups
            for i in range(3):
                time.sleep(0.1)  # Ensure different timestamps (increased delay)
                updated_data = pd.DataFrame({'col1': [1, i+2], 'col2': ['test', f'update_{i}']})
                
                with locked_file_write(test_file) as file_path:
                    updated_data.to_csv(file_path, index=False)
            
            # Verify backups were created (may be fewer than writes due to timestamp granularity)
            backup_files = list(backup_dir.glob("test_*.csv"))
            assert len(backup_files) >= 1  # At least one backup should exist
            
            # Test cleanup function
            # Set very short keep_days to clean up everything
            cleanup_old_backups(backup_dir, "test_*.csv", keep_days=0)
            
            # All backups should be cleaned up (since keep_days=0)
            remaining_files = list(backup_dir.glob("test_*.csv"))
            assert len(remaining_files) == 0
    
    def test_write_failure_restoration(self):
        """Test that failed writes are restored from backup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "data" / "processed" / "test.csv"
            
            # Create initial file
            test_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = pd.DataFrame({'col1': [1], 'col2': ['original']})
            initial_data.to_csv(test_file, index=False)
            original_content = test_file.read_text()
            
            # Attempt write that fails
            try:
                with locked_file_write(test_file) as file_path:
                    # Write some content
                    bad_data = "This is not valid CSV content"
                    file_path.write_text(bad_data)
                    # Simulate failure
                    raise ValueError("Simulated write failure")
                    
            except ValueError:
                pass  # Expected
            
            # File should be restored to original content
            restored_content = test_file.read_text()
            assert restored_content == original_content
            
            # Verify data is intact
            restored_data = pd.read_csv(test_file)
            pd.testing.assert_frame_equal(restored_data, initial_data)