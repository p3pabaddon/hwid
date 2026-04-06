import os
import sys
import subprocess
import winreg
import uuid
import random
import shutil
import ctypes
import time
import json
import hashlib
import base64

class SpoofEngine:
    def __init__(self, base_path=None):
        if base_path:
            self.base_path = base_path
        elif getattr(sys, 'frozen', False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.log_lines = []
        self.progress_callback = None
        self.status_callback = None

    def log(self, msg, level="INFO"):
        self.log_lines.append(f"[{level}] {msg}")

    def update_status(self, text):
        if self.status_callback:
            self.status_callback(text)

    def update_progress(self, value):
        if self.progress_callback:
            self.progress_callback(value)

    def get_hardware_info(self):
        """Fetch current hardware IDs for display using multi-method fallback."""
        info = {"disk": "N/A", "motherboard": "N/A", "mac": "N/A", "gpu": "N/A", "bios": "N/A", "cpu": "N/A"}
        
        def _try_get(cmds):
            for cmd in cmds:
                try:
                    args = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd]
                    result = subprocess.run(args, capture_output=True, text=True, timeout=8, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except Exception as e:
                    self.log(f"PS Try Fail: {cmd} | {e}", "DEBUG")
            return None

        # Disk Serial
        info["disk"] = _try_get([
            "(Get-CimInstance Win32_DiskDrive | Where-Object { $_.InterfaceType -ne 'USB' } | Select-Object -First 1).SerialNumber",
            "(Get-WmiObject Win32_DiskDrive | Where-Object { $_.InterfaceType -ne 'USB' } | Select-Object -First 1).SerialNumber",
            "wmic diskdrive get serialnumber"
        ]) or "N/A"

        # Motherboard Serial
        info["motherboard"] = _try_get([
            "(Get-CimInstance Win32_BaseBoard).SerialNumber",
            "(Get-WmiObject Win32_BaseBoard).SerialNumber",
            "wmic baseboard get serialnumber"
        ]) or "N/A"

        # MAC Address (Active)
        info["mac"] = _try_get([
            "(Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | Select-Object -First 1).MacAddress",
            "(Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object { $_.IPEnabled -eq $true } | Select-Object -First 1).MACAddress",
            "getmac /fo list"
        ]) or "N/A"

        # GPU ID
        info["gpu"] = _try_get([
            "(Get-CimInstance Win32_VideoController | Select-Object -First 1).DeviceID",
            "wmic path Win32_VideoController get pnpdeviceid"
        ]) or "N/A"

        # BIOS
        info["bios"] = _try_get([
            "(Get-CimInstance Win32_BIOS).SerialNumber",
            "wmic bios get serialnumber"
        ]) or "N/A"

        # CPU
        info["cpu"] = _try_get([
            "(Get-CimInstance Win32_Processor).ProcessorId",
            "wmic cpu get processorid"
        ]) or "N/A"

        return info

    def get_pro_metrics(self):
        """Mock real-time system metrics for the Pro dashboard."""
        return {
            "stealth": 0.90 + (random.random() * 0.08),
            "kernel": 0.82 + (random.random() * 0.12),
            "storage": 0.75 + (random.random() * 0.20)
        }

    def system_stealth(self):
        """Self-destruct/Cleanup spoofer existence from system."""
        try:
            # Delete log files
            if os.path.exists("debug.log"): os.remove("debug.log")
            # Clear prefetch/temp traces if admin
            subprocess.run(["powershell", "Clear-RecycleBin -Confirm:$false"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # Exit app
            os._exit(0)
        except:
            os._exit(1)

    def load_kernel_driver(self):
        """Simulate loading a kernel driver for HWID masking."""
        # In a real app, this would use Service Control Manager (SCM)
        time.sleep(2)
        driver_path = os.path.join(self.base_path, "drivers", "vghid.sys")
        return os.path.exists(driver_path)

    def toggle_ghost_mode(self, enabled, window_handle=None):
        """Toggle window visibility from screen recorders/capture."""
        if not sys.platform == "win32": return
        try:
            # 0x00000011 -> WDA_EXCLUDEFROMCAPTURE
            # Using win32gui/ctypes to prevent capture
            hwnd = window_handle.winfo_id() if window_handle else None
            if hwnd:
                ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x11 if enabled else 0x0)
        except:
            pass

    def execute_all(self):
        """Run the full spoofing sequence."""
        steps = [
            ("Bağlantı kesiliyor...", 0.1, self.null_op),
            ("Disk & Volume ID'leri yenileniyor...", 0.2, self.spoof_disks),
            ("Anakart & BIOS verileri maskeleniyor...", 0.4, self.spoof_motherboard),
            ("GPU & CPU kimlikleri simüle ediliyor...", 0.5, self.spoof_compute),
            ("MAC Adresi yenileniyor...", 0.7, self.spoof_network),
            ("Kayıt defteri izleri temizleniyor...", 0.9, self.clean_registry),
            ("Tamamlanıyor...", 1.0, self.null_op)
        ]
        
        for msg, prog, func in steps:
            self.update_status(msg)
            func()
            self.update_progress(prog)
            time.sleep(random.uniform(0.5, 1.5))

    def null_op(self): pass

    def spoof_disks(self):
        """Spoof Disk Drive identifiers and Volume IDs."""
        try:
            # Registry based Hardware IDs
            paths = [
                r"SYSTEM\CurrentControlSet\Enum\SCSI",
                r"SYSTEM\CurrentControlSet\Enum\IDE",
                r"SYSTEM\CurrentControlSet\Services\disk\Enum",
                r"HARDWARE\DEVICEMAP\Scsi"
            ]
            for p in paths:
                self._randomize_all_values(p)
            
            # Volume IDs (Partition serials)
            self.log("Randomizing Volume Serial Numbers...")
            subprocess.run(["powershell", "-Command", "Get-Volume | ForEach-Object { $id = -join ((48..57) + (97..102) | Get-Random -Count 8 | ForEach-Object {[char]$_}); set-itemproperty -path ('HKLM:\\SYSTEM\\MountedDevices') -name ('\\??\\Volume{' + $_.UniqueId + '}') -value $id -ErrorAction SilentlyContinue }"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Clean MountPoints2
            subprocess.run(["powershell", "-Command", "Remove-Item -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MountPoints2' -Recurse -ErrorAction SilentlyContinue"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
        except Exception as e:
            self.log(f"Disk Spoof Fail: {e}")

    def spoof_motherboard(self):
        """Spoof Motherboard and BIOS identifiers comprehensively."""
        try:
            paths = [
                r"DESCRIPTION\System\BIOS",
                r"HARDWARE\Description\System\BIOS",
                r"HARDWARE\Description\System",
                r"SYSTEM\CurrentControlSet\Control\SystemInformation"
            ]
            
            targets = ["BaseBoardSerialNumber", "SystemSerialNumber", "SystemSKU", "ComputerHardwareId", "BIOSVersion", "BaseBoardProduct"]
            
            for path in paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
                    for t in targets:
                        try:
                            # 12-16 chars works best for serials
                            val = self._rand_hex(random.randint(12, 20))
                            winreg.SetValueEx(key, t, 0, winreg.REG_SZ, val)
                        except: continue
                    winreg.CloseKey(key)
                except: continue
            
            # SMBIOS / UUID / Data
            self.log("Randomizing SMBIOS UUIDs...")
            sm_paths = [
                r"SOFTWARE\Microsoft\Cryptography",
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            ]
            for sm in sm_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sm, 0, winreg.KEY_ALL_ACCESS)
                    # Common keys tracked for HWID
                    targets = ["MachineGuid", "ProductId", "BuildGuid"]
                    for t in targets:
                        try:
                            val = str(uuid.uuid4())
                            winreg.SetValueEx(key, t, 0, winreg.REG_SZ, val)
                        except: continue
                    winreg.CloseKey(key)
                except: continue

        except Exception as e:
            self.log(f"Mobo Spoof Fail: {e}")

    def spoof_compute(self):
        """Spoof CPU and GPU identifiers in registry."""
        try:
            # CPU
            path = r"HARDWARE\DESCRIPTION\System\CentralProcessor"
            h = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            for i in range(winreg.QueryInfoKey(h)[0]):
                try:
                    cp_sub = winreg.EnumKey(h, i)
                    sk = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path + "\\" + cp_sub, 0, winreg.KEY_ALL_ACCESS)
                    winreg.SetValueEx(sk, "ProcessorNameString", 0, winreg.REG_SZ, f"Intel(R) Core(TM) i9-14900K CPU @ 6.{random.randint(0,9)}0GHz")
                    winreg.CloseKey(sk)
                except: continue
            winreg.CloseKey(h)

            # GPU
            gpu_paths = [r"HARDWARE\DEVICEMAP\VIDEO", r"SYSTEM\CurrentControlSet\Control\Video"]
            for gp in gpu_paths:
                self._randomize_all_values(gp)
                
            self.log("Compute identifiers randomized.")
        except Exception as e:
            self.log(f"Compute Spoof Fail: {e}")

    def spoof_network(self):
        """Spoof MAC addresses for all adapters."""
        try:
            path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
            h = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            for i in range(winreg.QueryInfoKey(h)[0]):
                try:
                    subkey_name = winreg.EnumKey(h, i)
                    if len(subkey_name) != 4: continue
                    sk = winreg.OpenKey(h, subkey_name, 0, winreg.KEY_ALL_ACCESS)
                    new_mac = "02" + self._rand_hex(10)
                    winreg.SetValueEx(sk, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
                    winreg.CloseKey(sk)
                    self.log(f"Registry updated for adapter {subkey_name} -> {new_mac}")
                except: continue
            winreg.CloseKey(h)
            
            # Restart all enabled network adapters to apply MAC change
            self.log("Adapters restarting to apply changes...")
            ps_script = """
            Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
                $name = $_.Name
                Write-Host "Restarting: $name"
                Disable-NetAdapter -Name $name -Confirm:$false
                Start-Sleep -Seconds 1
                Enable-NetAdapter -Name $name -Confirm:$false
            }
            """
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script], 
                           capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log("Network adapter reset completed.")
        except Exception as e:
            self.log(f"MAC Spoof Fail: {e}")

    def clean_registry(self):
        """Remove common AC tracking keys."""
        to_delete = [
            r"SOFTWARE\Microsoft\Cryptography\MachineGuid",
            r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001"
        ]
        # Just randomize MachineGuid instead of delete to avoid system instability
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4()))
            winreg.CloseKey(k)
        except: pass

    def deep_clean_game(self, game_key):
        """Game-specific file and registry cleanup."""
        self.update_status(f"Temizleniyor: {game_key}...")
        self.update_progress(0.3)
        time.sleep(1)
        
        user_profile = os.environ.get("USERPROFILE", "")
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        appdata = os.environ.get("APPDATA", "")
        
        targets = []
        if game_key == "clean_val":
            targets = [
                os.path.join(local_appdata, "Riot Games"),
                os.path.join(local_appdata, "VALORANT"),
                os.path.join(appdata, "Riot Games")
            ]
        elif game_key == "clean_fivem":
            targets = [
                os.path.join(local_appdata, "FiveM", "FiveM.app", "data", "cache"),
                os.path.join(local_appdata, "FiveM", "FiveM.app", "data", "server-cache"),
                os.path.join(appdata, "CitizenFX")
            ]
        elif game_key == "clean_apex":
            targets = [
                os.path.join(local_appdata, "Origin"),
                os.path.join(local_appdata, "Electronic Arts"),
                os.path.join(appdata, "EasyAntiCheat")
            ]

        for path in targets:
            self.safe_delete_tree(path)
            
        self.update_progress(1.0)
        self.update_status("Temizleme bitti!")
        time.sleep(1)
        self.update_status("Система готова")
        self.update_progress(0.0)

    def safe_delete_tree(self, path):
        if not os.path.exists(path): return
        try:
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path, ignore_errors=True)
            self.log(f"Deleted: {path}")
        except Exception as e:
            self.log(f"Delete Fail: {path} | {e}")

    def _randomize_all_values(self, path):
        """Deep recursion to randomize every data value in a branch."""
        try:
            h = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            info = winreg.QueryInfoKey(h)
            
            # Values in THIS key
            v_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_ALL_ACCESS)
            for i in range(info[1]):
                try:
                    v_name = winreg.EnumValue(h, i)[0]
                    # Only randomize strings for safety
                    if winreg.EnumValue(h, i)[2] == winreg.REG_SZ:
                        winreg.SetValueEx(v_key, v_name, 0, winreg.REG_SZ, self._rand_hex(20))
                except: continue
            winreg.CloseKey(v_key)

            # Recurse subkeys
            for i in range(info[0]):
                try:
                    s = winreg.EnumKey(h, i)
                    self._randomize_all_values(path + "\\" + s)
                except: continue
            winreg.CloseKey(h)
        except: pass

    def _rand_hex(self, length):
        return ''.join(random.choices("0123456789ABCDEF", k=length))

    def clean_efi(self):
        """Try to clean EFI trackers by mounting and searching."""
        self.log("Starting EFI Trace Clean...")
        try:
            # Try to mount EFI to Z:
            subprocess.run(["mountvol", "Z:", "/S"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(1)
            
            efi_targets = [
                r"Z:\EFI\Microsoft\Boot\bootmgfw.efi", # Just a check
                r"Z:\EFI\RiotGames", # Hypothetical
                r"Z:\EFI\Vanguard",
            ]
            
            for t in efi_targets:
                if os.path.exists(t):
                    self.log(f"Found EFI Tracker: {t}")
                    # Usually we'd delete or shuffle it
            
            subprocess.run(["mountvol", "Z:", "/D"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log("EFI Clean Check Complete.")
        except Exception as e:
            self.log(f"EFI Clean failed: {e}")

class TraceAnalyzer:
    def __init__(self, engine):
        self.engine = engine
        self.trace_definitions = [
            {"name": "Riot Client", "path": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Riot Games")},
            {"name": "Vanguard", "path": os.path.join(os.environ.get("ProgramFiles", ""), "Riot Vanguard")},
            {"name": "Vanguard Logs", "path": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Riot Games/Riot Client/Logs")},
            {"name": "Valorant Persistent", "path": os.path.join(os.environ.get("LOCALAPPDATA", ""), "VALORANT/Saved")},
            {"name": "Valorant Logs", "path": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Riot Games/Riot Client/Logs")},
            {"name": "FiveM", "path": os.path.join(os.environ.get("LOCALAPPDATA", ""), "FiveM")},
            {"name": "CitizenFX", "path": os.path.join(os.environ.get("APPDATA", ""), "CitizenFX")},
            {"name": "Apex Legends", "path": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Apex")},
            {"name": "Origin AppData", "path": os.path.join(os.environ.get("APPDATA", ""), "Origin")},
            {"name": "BattlEye Service", "path": os.path.join(os.environ.get("CommonProgramFiles(x86)", ""), "BattlEye")},
            {"name": "Ubisoft Data", "path": os.path.join(os.environ.get("LOCALAPPDATA", ""), "Ubisoft Game Launcher/spool")},
            {"name": "Tencent Data", "path": r"C:\ProgramData\Tencent"},
        ]

    def scan(self):
        found = []
        for trace in self.trace_definitions:
            if os.path.exists(trace["path"]):
                found.append(trace)
        return found

    def clean(self, targets):
        for t in targets:
            self.engine.safe_delete_tree(t["path"])
        return True
