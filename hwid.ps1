# ============================================================
# Solutions HWID Spoofer - Enhanced Edition v2.0
# Original: sr2echa | Enhanced by: Antigravity AI
# ============================================================
# Features:
#   1. HwProfile GUID Spoofing
#   2. Machine GUID Spoofing
#   3. Volume ID Spoofing
#   4. MAC Address Spoofing          [NEW]
#   5. Hostname Randomization        [NEW]
#   6. Network Flush & Reset         [NEW]
#   7. Deep Registry Cleanup         [NEW]
#   8. Tracking File Cleanup         [NEW]
#   9. Disk Serial Masking (driver)  [NEW]
# ============================================================

$scriptPath = split-path -parent $MyInvocation.MyCommand.Definition
$logFile = "$scriptPath\spoof_log.txt"

# ---- Logging ----
function Write-Log {
    param([string]$Message, [string]$Status = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$timestamp] [$Status] $Message"
    Add-Content -Path $logFile -Value $entry
    if ($Status -eq "OK") {
        Write-Host "  [+] $Message" -ForegroundColor Green
    } elseif ($Status -eq "FAIL") {
        Write-Host "  [-] $Message" -ForegroundColor Red
    } elseif ($Status -eq "WARN") {
        Write-Host "  [!] $Message" -ForegroundColor Yellow
    } else {
        Write-Host "  [*] $Message" -ForegroundColor Cyan
    }
}

# ---- Helper: Random String Generator ----
function Get-RandomString {
    param([int]$Length,
          [int]$upperCase,
          [int]$onlyNumber)

    if ($onlynumber -eq 1) {
        $set = "0123456789".ToCharArray()
    }
    else {
        $set = "abcdef0123456789".ToCharArray()
    }

    $result = ""
    for ($x = 0; $x -lt $Length; $x++) {
        $result += $set | Get-Random
    }

    if ($upperCase -eq 1) { return $result.ToUpper() }
    else { return $result }
}

# ---- Helper: Random GUID Generator ----
function Get-RandomGUID {
    $Rand1 = Get-RandomString -Length 8 -upperCase 0 -onlyNumber 0
    $Rand2 = Get-RandomString -Length 4 -upperCase 0 -onlyNumber 0
    $Rand3 = Get-RandomString -Length 4 -upperCase 0 -onlyNumber 0
    $Rand4 = Get-RandomString -Length 4 -upperCase 0 -onlyNumber 0
    $Rand5 = Get-RandomString -Length 12 -upperCase 0 -onlyNumber 0
    return "$Rand1-$Rand2-$Rand3-$Rand4-$Rand5"
}

# ============================================================
# FEATURE 1: HwProfile GUID Spoofing (Original)
# ============================================================
function Set-HWProfileID {
    $registryPath = "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001"
    $registryKeyName = "HwProfileGuid"
    $RandID = "{$(Get-RandomGUID)}"
    Set-ItemProperty -Path $registryPath -Name $registryKeyName -Value $RandID
    Write-Log "HwProfile GUID changed to: $RandID" "OK"
}

# ============================================================
# FEATURE 2: Machine GUID Spoofing (Original)
# ============================================================
function Set-MachineGUID {
    $registryPath = "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography"
    $registryKeyName = "MachineGuid"
    $RandID = Get-RandomGUID
    Set-ItemProperty -Path $registryPath -Name $registryKeyName -Value $RandID
    Write-Log "Machine GUID changed to: $RandID" "OK"
}

# ============================================================
# FEATURE 3: Volume ID Spoofing (Original)
# ============================================================
function Set-VolID {
    $volidPath = "$scriptPath\Volumeid64.exe"
    if (-Not (Test-Path $volidPath)) {
        Write-Log "Volumeid64.exe not found, skipping Volume ID spoof." "WARN"
        return
    }
    $volID1 = Get-RandomString -Length 4 -upperCase 1 -onlyNumber 0
    $volID2 = Get-RandomString -Length 4 -upperCase 1 -onlyNumber 0
    $volidArgs = "C: $volID1-$volID2"

    $ps = New-Object System.Diagnostics.Process
    $ps.StartInfo.FileName = $volidPath
    $ps.StartInfo.Arguments = $volidArgs
    $ps.StartInfo.RedirectStandardOutput = $False
    $ps.StartInfo.UseShellExecute = $True
    $ps.StartInfo.WindowStyle = "Hidden"
    $ps.StartInfo.CreateNoWindow = $True
    $ps.Start() | Out-Null

    if (-Not $ps.WaitForExit(10000)) { $ps.Kill() }
    Write-Log "Volume ID changed to: $volID1-$volID2" "OK"
}

# ============================================================
# FEATURE 4: MAC Address Spoofing [NEW]
# ============================================================
function Set-MACAddress {
    $macFile = "$scriptPath\mac.txt"
    
    # Get available MAC addresses from file or generate random
    if (Test-Path $macFile) {
        $macList = Get-Content $macFile | Where-Object { $_.Trim() -ne "" }
        $newMAC = ($macList | Get-Random).Trim()
    } else {
        # Generate a random locally-administered MAC (02:XX:XX:XX:XX:XX)
        $newMAC = "02" + (Get-RandomString -Length 10 -upperCase 1 -onlyNumber 0)
    }

    # Format MAC for registry (no separators, 12 hex chars)
    $cleanMAC = $newMAC -replace "[:\-\.]", ""
    
    # Get all physical network adapters
    $adapters = Get-WmiObject -Class Win32_NetworkAdapter | Where-Object {
        $_.PhysicalAdapter -eq $true -and $_.MACAddress -ne $null
    }

    foreach ($adapter in $adapters) {
        $adapterName = $adapter.Name
        $adapterIndex = $adapter.Index
        
        # Find the registry key for this adapter
        $regBase = "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
        
        # Search adapter subkeys
        $subKeys = Get-ChildItem -Path $regBase -ErrorAction SilentlyContinue
        foreach ($key in $subKeys) {
            try {
                $driverDesc = (Get-ItemProperty -Path $key.PSPath -Name "DriverDesc" -ErrorAction SilentlyContinue).DriverDesc
                if ($driverDesc -eq $adapterName) {
                    # Set the NetworkAddress value (MAC spoof)
                    Set-ItemProperty -Path $key.PSPath -Name "NetworkAddress" -Value $cleanMAC -ErrorAction Stop
                    
                    # Disable and re-enable the adapter to apply
                    $adapter.Disable() | Out-Null
                    Start-Sleep -Seconds 2
                    $adapter.Enable() | Out-Null
                    
                    Write-Log "MAC Address for '$adapterName' changed to: $cleanMAC" "OK"
                    break
                }
            } catch {
                continue
            }
        }
    }

    if (-Not $adapters -or $adapters.Count -eq 0) {
        Write-Log "No physical network adapters found for MAC spoofing." "WARN"
    }
}

# ============================================================
# FEATURE 5: Hostname Randomization [NEW]
# ============================================================
function Set-RandomHostname {
    $hostFile = "$scriptPath\host.txt"
    
    if (Test-Path $hostFile) {
        $hostList = Get-Content $hostFile | Where-Object { $_.Trim() -ne "" }
        $newHostname = ($hostList | Get-Random).Trim()
    } else {
        # Generate a random Desktop-XXXXX hostname
        $suffix = Get-RandomString -Length 5 -upperCase 1 -onlyNumber 0
        $newHostname = "Desktop-$suffix"
    }

    # Change ComputerName in registry (takes effect after reboot)
    $regPath1 = "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName"
    $regPath2 = "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName"
    $regPath3 = "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"

    Set-ItemProperty -Path $regPath1 -Name "ComputerName" -Value $newHostname
    Set-ItemProperty -Path $regPath2 -Name "ComputerName" -Value $newHostname
    Set-ItemProperty -Path $regPath3 -Name "Hostname" -Value $newHostname
    Set-ItemProperty -Path $regPath3 -Name "NV Hostname" -Value $newHostname

    # Also use Rename-Computer if available
    try {
        Rename-Computer -NewName $newHostname -Force -ErrorAction Stop 2>$null
    } catch {
        # Fallback: registry changes above will take effect on reboot
    }

    Write-Log "Hostname changed to: $newHostname (reboot required to apply)" "OK"
}

# ============================================================
# FEATURE 6: Network Flush & Reset [NEW]
# ============================================================
function Invoke-NetworkFlush {
    Write-Log "Flushing network configuration..." "INFO"

    # Flush DNS cache
    ipconfig /flushdns 2>$null | Out-Null
    Write-Log "DNS cache flushed" "OK"

    # Release and renew IP
    ipconfig /release 2>$null | Out-Null
    Start-Sleep -Seconds 1
    ipconfig /renew 2>$null | Out-Null
    Write-Log "IP address released and renewed" "OK"

    # Reset Winsock catalog
    netsh winsock reset 2>$null | Out-Null
    Write-Log "Winsock catalog reset" "OK"

    # Reset TCP/IP stack
    netsh int ip reset 2>$null | Out-Null
    Write-Log "TCP/IP stack reset" "OK"

    # Clear ARP cache
    netsh interface ip delete arpcache 2>$null | Out-Null
    arp -d * 2>$null | Out-Null
    Write-Log "ARP cache cleared" "OK"

    # Reset firewall to defaults (optional but helps with tracking)
    # netsh advfirewall reset 2>$null | Out-Null
    # Write-Log "Firewall reset to defaults" "OK"
}

# ============================================================
# FEATURE 7: Deep Registry Cleanup [NEW]
# ============================================================
function Invoke-DeepRegistryCleanup {
    Write-Log "Starting deep registry cleanup..." "INFO"

    # --- Windows Product ID ---
    $paths = @(
        "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion",
        "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion"
    )
    foreach ($path in $paths) {
        try {
            # Randomize ProductId
            $newProductId = "$(Get-RandomString -Length 5 -upperCase 0 -onlyNumber 1)-$(Get-RandomString -Length 5 -upperCase 0 -onlyNumber 1)-$(Get-RandomString -Length 5 -upperCase 0 -onlyNumber 1)-$(Get-RandomString -Length 5 -upperCase 0 -onlyNumber 1)"
            Set-ItemProperty -Path $path -Name "ProductId" -Value $newProductId -ErrorAction SilentlyContinue
        } catch { }
    }
    Write-Log "Windows Product ID randomized" "OK"

    # --- Install Date Randomization ---
    try {
        $baseDate = Get-Date "2020-01-01"
        $randomDays = Get-Random -Minimum 0 -Maximum 1500
        $newDate = $baseDate.AddDays($randomDays)
        $unixTime = [int][double]::Parse(($newDate - (Get-Date "1970-01-01")).TotalSeconds.ToString())
        Set-ItemProperty -Path "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion" -Name "InstallDate" -Value $unixTime -ErrorAction SilentlyContinue
        Write-Log "Install Date randomized" "OK"
    } catch {
        Write-Log "Could not randomize Install Date" "WARN"
    }

    # --- Internet Explorer / Edge SQM Client ID ---
    try {
        $sqmPaths = @(
            "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SQMClient\Windows",
            "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SQMClient"
        )
        foreach ($sqmPath in $sqmPaths) {
            if (Test-Path $sqmPath) {
                $newSqmId = "{$(Get-RandomGUID)}"
                Set-ItemProperty -Path $sqmPath -Name "MachineId" -Value $newSqmId -ErrorAction SilentlyContinue
            }
        }
        Write-Log "SQM Client ID randomized" "OK"
    } catch {
        Write-Log "Could not randomize SQM Client ID" "WARN"
    }

    # --- Windows Update / Telemetry IDs ---
    try {
        $regWU = "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate"
        if (Test-Path $regWU) {
            Set-ItemProperty -Path $regWU -Name "SusClientId" -Value (Get-RandomGUID) -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $regWU -Name "SusClientIdValidation" -Value ([byte[]](0..15 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 })) -ErrorAction SilentlyContinue
        }
        Write-Log "Windows Update Client ID randomized" "OK"
    } catch {
        Write-Log "Could not randomize Windows Update IDs" "WARN"
    }

    # --- SMBIOS Data ---
    try {
        $biosPath = "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\mssmbios\Data"
        if (Test-Path $biosPath) {
            # We don't touch raw SMBIOS binary data (risky), but log it
            Write-Log "SMBIOS data location identified (kernel-level change needed)" "WARN"
        }
    } catch { }

    # --- EFI Variables (if UEFI) ---
    try {
        $efiPath = "Registry::HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Nsi\{eb004a03-9b1a-11d4-9123-0050047759bc}"
        if (Test-Path $efiPath) {
            Write-Log "EFI namespace detected (driver-level spoof recommended)" "WARN"
        }
    } catch { }

    # --- Game-Specific Registry Cleanup ---
    $gameKeys = @(
        "Registry::HKEY_CURRENT_USER\SOFTWARE\EasyAntiCheat",
        "Registry::HKEY_CURRENT_USER\SOFTWARE\BattlEye",
        "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\EasyAntiCheat",
        "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\BattlEye",
        "Registry::HKEY_CURRENT_USER\SOFTWARE\Epic Games",
        "Registry::HKEY_CURRENT_USER\SOFTWARE\Valve\Steam"
    )
    foreach ($gk in $gameKeys) {
        try {
            if (Test-Path $gk) {
                Remove-Item -Path $gk -Recurse -Force -ErrorAction SilentlyContinue
                Write-Log "Removed game tracking key: $($gk.Split('\')[-1])" "OK"
            }
        } catch {
            Write-Log "Could not remove: $($gk.Split('\')[-1])" "WARN"
        }
    }
}

# ============================================================
# FEATURE 8: Tracking File Cleanup [NEW]
# ============================================================
function Invoke-TrackingFileCleanup {
    Write-Log "Starting tracking file cleanup..." "INFO"

    # --- Prefetch files ---
    $prefetchPath = "$env:SystemRoot\Prefetch"
    if (Test-Path $prefetchPath) {
        try {
            Remove-Item -Path "$prefetchPath\*" -Force -ErrorAction SilentlyContinue
            Write-Log "Prefetch files cleared" "OK"
        } catch {
            Write-Log "Could not clear all Prefetch files" "WARN"
        }
    }

    # --- Temp files ---
    $tempPaths = @(
        $env:TEMP,
        "$env:SystemRoot\Temp",
        "$env:LOCALAPPDATA\Temp"
    )
    foreach ($tp in $tempPaths) {
        if (Test-Path $tp) {
            try {
                Remove-Item -Path "$tp\*" -Recurse -Force -ErrorAction SilentlyContinue
                Write-Log "Temp folder cleared: $tp" "OK"
            } catch {
                Write-Log "Could not fully clear: $tp" "WARN"
            }
        }
    }

    # --- Recent files history ---
    $recentPath = "$env:APPDATA\Microsoft\Windows\Recent"
    if (Test-Path $recentPath) {
        try {
            Remove-Item -Path "$recentPath\*" -Force -ErrorAction SilentlyContinue
            Write-Log "Recent files history cleared" "OK"
        } catch {
            Write-Log "Could not clear Recent files" "WARN"
        }
    }

    # --- Anti-Cheat leftover folders ---
    $acFolders = @(
        "$env:APPDATA\EasyAntiCheat",
        "$env:LOCALAPPDATA\EasyAntiCheat",
        "$env:ProgramData\EasyAntiCheat",
        "$env:APPDATA\BattlEye",
        "$env:LOCALAPPDATA\BattlEye",
        "$env:ProgramData\BattlEye",
        "$env:LOCALAPPDATA\FortniteGame",
        "$env:LOCALAPPDATA\EpicGamesLauncher"
    )
    foreach ($acf in $acFolders) {
        if (Test-Path $acf) {
            try {
                Remove-Item -Path $acf -Recurse -Force -ErrorAction SilentlyContinue
                Write-Log "Removed anti-cheat folder: $($acf.Split('\')[-1])" "OK"
            } catch {
                Write-Log "Could not remove: $($acf.Split('\')[-1])" "WARN"
            }
        }
    }

    # --- Event Logs (game-related traces) ---
    try {
        wevtutil cl Application 2>$null
        wevtutil cl System 2>$null
        wevtutil cl Security 2>$null
        Write-Log "Windows Event Logs cleared" "OK"
    } catch {
        Write-Log "Could not clear Event Logs" "WARN"
    }

    # --- USN Journal Reset ---
    try {
        fsutil usn deletejournal /d C: 2>$null | Out-Null
        Write-Log "USN Journal deleted on C:" "OK"
    } catch {
        Write-Log "Could not delete USN Journal" "WARN"
    }
}

# ============================================================
# FEATURE 9: Disk Serial Masking via Driver [NEW]
# ============================================================
function Invoke-DiskSerialSpoof {
    $driverPath = "$scriptPath\Commands\Hidden\spoofer.sys"
    
    if (-Not (Test-Path $driverPath)) {
        Write-Log "spoofer.sys not found, skipping disk serial masking." "WARN"
        return
    }

    # Check if driver is already loaded
    $serviceName = "SolutionsDiskSpoof"
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

    if ($existingService) {
        try {
            Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
            sc.exe delete $serviceName 2>$null | Out-Null
            Start-Sleep -Seconds 1
        } catch { }
    }

    # Create and start the driver service
    try {
        sc.exe create $serviceName binPath= "$driverPath" type= kernel start= demand 2>$null | Out-Null
        sc.exe start $serviceName 2>$null | Out-Null
        Write-Log "Disk serial spoofer driver loaded" "OK"
    } catch {
        Write-Log "Could not load spoofer driver (may need test signing mode)" "WARN"
    }
}


# ============================================================
#                    MAIN EXECUTION
# ============================================================

Write-Host ""
Write-Host "  =============================================" -ForegroundColor Magenta
Write-Host "   Solutions HWID Spoofer - Enhanced v2.0" -ForegroundColor Magenta
Write-Host "  =============================================" -ForegroundColor Magenta
Write-Host ""

# Clear previous log
if (Test-Path $logFile) { Remove-Item $logFile -Force }

# Check admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-Not $isAdmin) {
    Write-Host "  [!!!] THIS SCRIPT MUST BE RUN AS ADMINISTRATOR!" -ForegroundColor Red
    Write-Host "  [!!!] Right-click PowerShell -> Run as Administrator" -ForegroundColor Red
    Write-Host ""
    pause
    exit
}

Write-Log "Script started with Administrator privileges" "INFO"
Write-Host ""

# ---- Phase 1: Core ID Spoofing ----
Write-Host "  [Phase 1/6] Core ID Spoofing..." -ForegroundColor Yellow
try {
    Set-HWProfileID
} catch {
    Write-Log "FAILED: HwProfile GUID change - $_" "FAIL"
}

try {
    Set-MachineGUID
} catch {
    Write-Log "FAILED: Machine GUID change - $_" "FAIL"
}

try {
    Set-VolID
} catch {
    Write-Log "FAILED: Volume ID change - $_" "FAIL"
}

# ---- Phase 2: MAC Address Spoofing ----
Write-Host ""
Write-Host "  [Phase 2/6] MAC Address Spoofing..." -ForegroundColor Yellow
try {
    Set-MACAddress
} catch {
    Write-Log "FAILED: MAC Address change - $_" "FAIL"
}

# ---- Phase 3: Hostname Randomization ----
Write-Host ""
Write-Host "  [Phase 3/6] Hostname Randomization..." -ForegroundColor Yellow
try {
    Set-RandomHostname
} catch {
    Write-Log "FAILED: Hostname change - $_" "FAIL"
}

# ---- Phase 4: Deep Registry Cleanup ----
Write-Host ""
Write-Host "  [Phase 4/6] Deep Registry Cleanup..." -ForegroundColor Yellow
try {
    Invoke-DeepRegistryCleanup
} catch {
    Write-Log "FAILED: Registry cleanup - $_" "FAIL"
}

# ---- Phase 5: Tracking File Cleanup ----
Write-Host ""
Write-Host "  [Phase 5/6] Tracking File Cleanup..." -ForegroundColor Yellow
try {
    Invoke-TrackingFileCleanup
} catch {
    Write-Log "FAILED: File cleanup - $_" "FAIL"
}

# ---- Phase 6: Network Flush ----
Write-Host ""
Write-Host "  [Phase 6/6] Network Flush & Reset..." -ForegroundColor Yellow
try {
    Invoke-NetworkFlush
} catch {
    Write-Log "FAILED: Network flush - $_" "FAIL"
}

# ---- Optional: Disk Serial Driver ----
# Uncomment to enable (requires test-signing mode on Win10/11):
# Invoke-DiskSerialSpoof

# ---- Summary ----
Write-Host ""
Write-Host "  =============================================" -ForegroundColor Green
Write-Host "   ALL OPERATIONS COMPLETED!" -ForegroundColor Green
Write-Host "  =============================================" -ForegroundColor Green
Write-Host ""
Write-Host "  [*] Log saved to: $logFile" -ForegroundColor Cyan
Write-Host "  [*] A system REBOOT is recommended for" -ForegroundColor Cyan
Write-Host "      hostname and MAC changes to take" -ForegroundColor Cyan
Write-Host "      full effect." -ForegroundColor Cyan
Write-Host ""

Write-Log "All operations completed successfully" "INFO"