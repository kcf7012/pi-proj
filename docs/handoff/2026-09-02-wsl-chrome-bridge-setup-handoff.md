# Handoff: WSL ↔ Windows Chrome DevTools Bridge 設置紀錄

> 建立日期:2026-09-02
> 交接給:未來維護者 / 自己(下次 WSL 環境重建時參考)
> 工作目錄:`/home/elan/pi-proj`(WSL 端)
> Windows 端工作目錄:`C:\Tools\wsl-chrome-bridge\`

## 1. 任務目標
在 WSL 2 環境中,讓 Linux 端工具(playwright-cli、curl 等)可以**透過 CDP**(Chrome DevTools Protocol)**控制 Windows 桌面上的 Chrome 視窗**。達成「WSL 內下指令,Windows 桌面看到瀏覽器操作」的同步效果。

### 子目標
- WSL 內可連線到 Windows Chrome 的 9222 port
- Chrome 開啟時帶 `--remote-debugging-port=9222`
- Windows Firewall 允許 WSL 介面 inbound 9222
- netsh portproxy 將 WSL 介面 IP:9222 轉送至 127.0.0.1:9222
- **以上全部在開機時自動建立**(使用者登入即生效)
- **冪等設計**(重複執行不損壞、可手動驗證)

## 2. 已完成內容

- ✅ 在 Windows 端建立完整檔案結構(見 §3)
- ✅ 驗證連線鏈路通暢(WSL curl → Chrome 9222 → 取得 CDP version 訊息)
- ✅ 確認 playwright-cli 可 attach 到 Windows Chrome 並截圖同步畫面
- ✅ 開機啟動器已放置於 Startup 資料夾,下次登入自動生效
- ✅ 冪等測試通過(portproxy/防火牆/Chrome listen 全部正確跳過)

## 3. 關鍵檔案和位置

| 檔案 | 用途 |
|------|------|
| `C:\Tools\wsl-chrome-bridge\Start-WslChromeBridge.ps1` | 主腳本(冪等、可重跑、log 到 bridge.log) |
| `C:\Tools\wsl-chrome-bridge\Stop-WslChromeBridge.ps1` | 解除安裝腳本(移除所有設定) |
| `C:\Tools\wsl-chrome-bridge\bridge.log` | 執行紀錄(會持續 append) |
| `C:\Users\Elan\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\WslChromeBridge.vbs` | 開機自動啟動器(背景、不彈窗) |

## 4. 重要規則和限制

- ⚠️ **WSL 介面別名寫死為 `vEthernet (WSL (Hyper-V firewall))`**,Win11 WSL2 預設介面。若 WSL 升級或介面名稱改變,腳本會在 log 報錯並退出(不會半毀狀態)
- ⚠️ **Chrome 152 有 bug:忽略 `--remote-debugging-address=0.0.0.0`**,永遠只 bind `127.0.0.1`。這是為什麼需要 netsh portproxy 介入
- ⚠️ **PowerShell 5.1 讀 .ps1 預設用 Windows-1252**,含中文註解必須用 **UTF-8 BOM** 編碼(踩過坑,見 §7)
- ⚠️ **PowerShell 把 `$var:$var` 解析為 scope**(冒號是 drive separator),必須寫成 `${var}:${var}`(踩過坑,見 §7)
- ⚠️ netsh portproxy **需要系統管理員 PowerShell** 才能新增;若忘記 `-RunAs Administrator` 會 silently 失敗
- ⚠️ Windows Defender Firewall 預設 **block** 9222 inbound;必須手動新增 allow 規則(踩過坑,見 §6 步驟 4)
- ⚠️ 若 Chrome 已 listen 9222,**腳本不會重啟**(避免中斷使用者 session);想強制重啟 → 加 `-Force` 參數
- ⚠️ **不要把 `Start-WslChromeBridge.ps1` 放到 Git repository 內**,這是 Windows 環境特定檔案(`C:\Tools\` 是 WSL mount 的 `/mnt/c/Tools/`)

## 5. 已確認結論

### ✓ 連線鏈路(已驗證 2026-09-02)

```
WSL bash 指令
    ↓
playwright-cli attach --cdp=http://172.21.208.1:9222
    ↓
WSL eth0 介面送出 HTTP 請求
    ↓
Windows Hyper-V vEthernet (WSL (Hyper-V firewall)) 介面 (172.21.208.1)
    ↓
netsh portproxy:172.21.208.1:9222 → 127.0.0.1:9222
    ↓
Windows Defender Firewall 規則 "WSL Chrome DevTools 9222" (allow inbound)
    ↓
Chrome --remote-debugging-port=9222 (PID 動態)
    ↓
回傳 CDP 訊息 + 控制 WebSocket
    ↓
Windows 桌面 Chrome 視窗即時更新
```

### ✓ 完整執行流程(已驗證)

1. **VBS 啟動器** 背景呼叫 PowerShell(`-WindowStyle Hidden`)
2. PowerShell 跑 `Start-WslChromeBridge.ps1`
3. ~8 秒內完成(若所有設定已存在且 Chrome 已 listen)
4. log 寫入 `C:\Tools\wsl-chrome-bridge\bridge.log`

### ✓ 冪等行為(已驗證)

重複執行 `Start-WslChromeBridge.ps1`:
- portproxy 已存在 → `portproxy 已存在,跳過: 172.21.208.1:9222 → 127.0.0.1:9222`
- 防火牆規則已存在 → `防火牆規則已存在,跳過: 'WSL Chrome DevTools 9222'`
- Chrome 已 listen 9222 → `Chrome 已 listen 9222 (PID XXXX),跳過啟動`

### ✓ 截圖同步已驗證

WSL 用 `playwright-cli screenshot --hires` 抓到的畫面 = Windows 桌面 Chrome 視窗實際內容(已驗證抓取 `https://www.anthropic.com/news` 頁面)。

## 6. 設置步驟(完整記錄,供未來重建參考)

### 步驟 1:WSLg 確認(2026-09-02 已驗證)

```bash
# WSL 內
echo $DISPLAY
# 應輸出 :0 或 :1 → 代表 WSLg 已啟用(Win11 預設)
```

### 步驟 2:Windows 端啟動 Chrome + bind 9222(2026-09-02 已驗證)

需在 PowerShell(不需 admin)執行:

```powershell
# 1. 強制關閉所有 Chrome(避免 user-data-dir 衝突)
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 2. 啟動 Chrome + 開遠端除錯 port
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --remote-debugging-address=0.0.0.0 `
  --remote-allow-origins=* `
  --no-first-run `
  --user-data-dir="C:\Temp\ChromeDebug" `
  https://www.anthropic.com/news
```

**踩坑記錄**:
- Chrome 152 忽略 `--remote-debugging-address=0.0.0.0`,仍只 bind `127.0.0.1`
- 直接從 WSL 連 `localhost:9222` 會失敗(WSL 2 不轉送 loopback)

### 步驟 3:新增防火牆規則(需 admin PowerShell)(2026-09-02 已驗證)

```powershell
# 系統管理員 PowerShell
netsh advfirewall firewall add rule `
  name="WSL Chrome DevTools 9222" `
  dir=in action=allow protocol=TCP localport=9222 profile=any

# 驗證
netsh advfirewall firewall show rule name="WSL Chrome DevTools 9222"
```

**踩坑記錄**:`New-NetFirewallRule` 在 PowerShell 5.1 行為不一致,改用 `netsh advfirewall` 跨版本穩定。

### 步驟 4:建立 netsh portproxy(需 admin PowerShell)(2026-09-02 已驗證)

WSL 介面 IP 是從 WSL 內 `ip route show default` 取得 default gateway `172.21.208.1`,在 Windows 端對應 `vEthernet (WSL (Hyper-V firewall))` 介面。

```powershell
# 系統管理員 PowerShell(先確認介面 IP)
$wslIP = (Get-NetIPAddress -InterfaceAlias 'vEthernet (WSL (Hyper-V firewall))' -AddressFamily IPv4).IPAddress
Write-Host "WSL 介面 IP: $wslIP"
# 預期輸出: WSL 介面 IP: 172.21.208.1

# 新增 portproxy
netsh interface portproxy add v4tov4 `
  listenaddress=$wslIP `
  listenport=9222 `
  connectaddress=127.0.0.1 `
  connectport=9222

# 驗證
netsh interface portproxy show v4tov4
```

**踩坑記錄**:`netsh interface portproxy` 需要 admin 權限,普通 PowerShell 會 silently 失敗。

### 步驟 5:建立檔案(2026-09-02 已完成)

詳見 §3。所有 .ps1 腳本需用 **UTF-8 BOM** 編碼(PowerShell 5.1 讀 .ps1 預設編碼為 Windows-1252,中文註解會解析失敗)。

### 步驟 6:驗證連線(2026-09-02 已驗證)

```bash
# WSL 內
curl http://172.21.208.1:9222/json/version
# 應輸出:
# {
#    "Browser": "Chrome/152.0.7977.65",
#    "Protocol-Version": "1.3",
#    ...
#    "webSocketDebuggerUrl": "ws://172.21.208.1:9222/devtools/browser/..."
# }

# WSL 內 attach 瀏覽器
playwright-cli attach --cdp=http://172.21.208.1:9222

# 驗證同步(從 WSL 截圖,對照 Windows 桌面視窗)
playwright-cli screenshot --filename=/tmp/test.png --hires
```

## 7. 開發過程踩坑記錄(PowerShell 陷阱)

### 坑 1:PowerShell 5.1 讀 .ps1 預設用 Windows-1252

**症狀**:`.ps1` 檔含中文註解,在 Windows PowerShell 5.1 執行時報錯 `ParserError`,中文顯示為 `?`。

**解法**:用 UTF-8 BOM 編碼存檔(`\xef\xbb\xbf` 開頭)。在 WSL/Linux 端寫檔後,手動加 BOM:

```bash
printf '\xef\xbb\xbf' > /tmp/bom
cat /tmp/bom /mnt/c/Tools/wsl-chrome-bridge/Start-WslChromeBridge.ps1 > /tmp/newfile
mv /tmp/newfile /mnt/c/Tools/wsl-chrome-bridge/Start-WslChromeBridge.ps1
```

### 坑 2:`$var:$var` 被 PowerShell 解析為 scope

**症狀**:腳本中 `"$wslIP:$DebugPort"` 報錯 `Variable reference is not valid. ':' was not followed by a valid variable name character`,PowerShell 把 `:` 視為 drive scope separator。

**解法**:用 `${}` 包住變數:

```powershell
# 錯誤
Write-Log "$wslIP:$DebugPort"

# 正確
Write-Log "${wslIP}:${DebugPort}"
```

### 坑 3:Chrome 152 忽略 `--remote-debugging-address`

**症狀**:即使加 `--remote-debugging-address=0.0.0.0`,Chrome 仍只 bind `127.0.0.1`。已確認是 Chrome 152 的 regression bug。

**解法**:不依賴 Chrome bind 0.0.0.0,改用 **netsh portproxy** 在 OS 層做轉送(WSL 介面 → loopback)。此方案不受 Chrome 版本影響。

### 坑 4:`Get-NetIPAddress -InterfaceAlias 'vEthernet (WSL)'` 找不到

**症狀**:Win11 WSL2 預設介面別名是 `vEthernet (WSL (Hyper-V firewall))`,不是 `vEthernet (WSL)`。

**解法**:用 `Get-NetAdapter` 查所有介面別名,確認正確名稱後寫入腳本。

### 坑 5:WSL 2 不轉送 loopback

**症狀**:從 WSL 連 `localhost:9222` 或 `127.0.0.1:9222` 永遠失敗。WSL 2 是 VM 架構,127.0.0.1 是 WSL 自己的 loopback,不會自動轉到 Windows。

**解法**:必須用 Windows host IP(`172.21.208.1`),且需有 portproxy + 防火牆規則介入。

### 坑 6:`netsh interface portproxy` 需要 admin 權限

**症狀**:在普通 PowerShell 執行 `netsh interface portproxy add ...` 會 silently 失敗,沒錯誤訊息但 `show v4tov4` 沒輸出。

**解法**:**必須**用「以系統管理員身分執行」的 PowerShell。

## 8. 日常使用指令

```bash
# WSL 內驗證橋接是否通
curl http://172.21.208.1:9222/json/version

# WSL 內 attach 瀏覽器
playwright-cli attach --cdp=http://172.21.208.1:9222

# WSL 內看 attach 狀態
playwright-cli list

# 想強制重啟 Chrome(例如 profile 卡住)
powershell -File 'C:\Tools\wsl-chrome-bridge\Start-WslChromeBridge.ps1' -Force

# 完全解除安裝(移除所有設定)
powershell -File 'C:\Tools\wsl-chrome-bridge\Stop-WslChromeBridge.ps1'

# 看啟動 log
cat /mnt/c/Tools/wsl-chrome-bridge/bridge.log
```

## 9. 注意事項

- 若 Chrome 跑得很順暢、session 持續中,**腳本不會動 Chrome**(避免中斷你的工作)—這是設計
- 想關 Chrome 重新乾淨啟動 → 加 `-Force` 參數
- 防火牆規則會持續存在(就算解除安裝前先手動刪也無妨,因為它是 idempotent)
- 若 WSL 升級、或介面別名改變,腳本會在 log 報錯並結束(不會半毀狀態)
- **不要把 `C:\Tools\wsl-chrome-bridge\` 加入 Git**,這是 Windows 環境特定檔案

## 10. 建議下一步

1. **觀察下次開機是否自動生效**:重啟 Windows 後,登入時應不會看到任何視窗(背景執行),但 30 秒內 `curl http://172.21.208.1:9222/json/version` 應能通
2. **若開機未生效**:檢查 `bridge.log` 看錯誤訊息;確認 Startup 資料夾的 `.vbs` 仍存在
3. **若 WSL 介面 IP 變動**(例如換網路):執行 `ip route show default` 取得新 IP,更新 `Start-WslChromeBridge.ps1` 的介面別名查詢邏輯
4. **若 Chrome 大版本升級後修好 `--remote-debugging-address=0.0.0.0` bug**:可考慮移除 portproxy + 防火牆規則,改用更簡潔的方案(但目前方案已穩定運作,不建議主動改)

---

**附錄**:本次 session 已驗證從 WSL `playwright-cli attach --cdp=http://172.21.208.1:9222` 成功控制 Windows 桌面 Chrome 視窗,並截圖同步畫面(`/home/elan/pi-proj/docs/handoff/wsl-chrome-attach-test.png`,383KB hi-res)。