import os
import subprocess

class LocalDiagnostics:
    
    @staticmethod
    def _execute_cmd(args):
        """Safely executes system commands without shell invocation."""
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error executing {' '.join(args)}: {e.stderr.strip()}"
        except FileNotFoundError:
            return f"System utility error: {' '.join(args)} is not installed or available in PATH."

    def get_memory_utilization(self):
        """Fetches and parses memory footprint from free."""
        print("Memory Allocation")
        raw_out = self._execute_cmd(["free", "-m"])
        lines = raw_out.strip().split("\n")
        
        # Parse and format
        for line in lines:
            if line.startswith("Mem:"):
                parts = line.split()
                total = int(parts[1])
                used = int(parts[2])
                free = int(parts[3])
                buff_cache = int(parts[5])
                
                used_pct = (used / total) * 100
                free_pct = (free / total) * 100
                
                report = (
                    f"Total Memory:       {total} MB\n"
                    f"Used Memory:        {used} MB ({used_pct:.2f}%)\n"
                    f"Free Memory:        {free} MB ({free_pct:.2f}%)\n"
                    f"Buffer/Cache:       {buff_cache} MB"
                )
                return report
        return "Could not parse memory information."

    def get_disk_utilization(self):
        """Fetches root disk usage from df."""
        print("Disk Filesystem Metrics")
        raw_out = self._execute_cmd(["df", "-h", "/"])
        lines = raw_out.strip().split("\n")
        if len(lines) >= 2:
            header = "Filesystem      Size  Used  Avail Use% Mounted"
            return f"{header}\n{lines[1]}"
        return "Could not parse disk execution parameters."

    def get_cpu_and_processes(self):
        """Fetches top 5 CPU consuming processes using ps."""
        print("Top 5 CPU Resource Consumers")
        
        raw_out = self._execute_cmd(["ps", "-eo", "pid,%cpu,%mem,comm", "--sort=-%cpu"])
        lines = raw_out.strip().split("\n")
        lines[0] = "    " + lines[0]
        return "\n".join(lines[:6])  


    def get_network_connections(self):
        """Counts active listening/established sockets via ss."""
        raw_out = self._execute_cmd(["ss", "-tuln"])
        lines = raw_out.strip().split("\n")
        listening_count = max(0, len(lines) - 1)
        return f"Active Network Sockets (Listening state): {listening_count}\n" + "\n".join(lines[:10])


class LogParser:
    """Extracts trend patterns and error metric thresholds out of flat-text system logs."""
    
    @staticmethod
    def calculate_error_frequencies(file_path):
        if not os.path.exists(file_path):
            return f"Target path verification failed: '{file_path}' does not exist."
        
        metrics = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
        total_lines = 0
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    total_lines += 1
                    upper_line = line.upper()
                    for severity in metrics.keys():
                        if severity in upper_line:
                            metrics[severity] += 1
            
            # Formatting 
            report = [f"--- Log Analysis Report for: {file_path} ---", f"Total Lines Scanned: {total_lines}"]
            for key, count in metrics.items():
                pct = (count / total_lines * 100) if total_lines > 0 else 0
                report.append(f" - [{key}]: Found {count} instances ({pct:.2f}%)")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"Failed processing log files safely: {str(e)}"
