import subprocess

def _run_ps(cmd):
    try:
        full_cmd = f'powershell -Command "{cmd}"'
        print(f"Running: {full_cmd}")
        out = subprocess.check_output(full_cmd, shell=True).decode("utf-8").strip()
        print(f"Output: '{out}'")
        return out
    except Exception as e:
        print(f"Error: {e}")
        return None

print("Testing Disk Serial:")
_run_ps("(Get-CimInstance Win32_DiskDrive | Select-Object -First 1).SerialNumber")

print("\nTesting UUID:")
_run_ps("(Get-CimInstance Win32_ComputerSystemProduct).UUID")

print("\nTesting MAC:")
_run_ps("(Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object -First 1).MacAddress")
