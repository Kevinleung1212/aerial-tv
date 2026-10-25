# Aerial 1.47 — Android 9–14 / 繁體中文（香港／粵語）定製

此定製功能位於 `feature/tvos-hant-android9-14`，原來的 `main` 不會自動改動。Fork 遵守上游 [MIT LICENSE](LICENSE)；Apple 航拍片源另有權利限制，**影片沒有打包到 APK**。

## 目前已包含

- 以原作者 Aerial 1.47 為基礎：玻璃底板、App 網格、長按 OK 管理、資料夾、隱藏及卸載入口、小米已知系統 App、控制中心、Bing／14 張壁紙、航拍／相片／時鐘／自選 MP4 屏保和個性化選項
- Aerial 1.47 手機頁：TV 相同的五列網格、拖動排序、App 改名／改圖示、資料夾、隱藏／還原、HDMI 圖示與手動名稱
- 新增 Android 正體中文語言資源：香港 `zh-HK`、澳門 `zh-MO`、臺灣 `zh-TW`、一般 `zh-Hant`。香港版主要使用繁體書面語，重點操作提示加少量廣東話措辭。
- 手機頁按 **手機瀏覽器的系統首選語言** 自動匹配上述區域，也可在「更多」手動選擇。TV 本身依 **電視 Android 系統語言** 選擇 Android 字串。
- 首次使用時預設：單排玻璃底板、第二排不偷看、右上角大時鐘、清晰高對比焦點。**已有用戶個人設定不會被覆蓋。**
- HDMI 若透過 Android TV Input Framework 的 CEC 子輸入回報例如 Apple TV、PS5、Switch 或 Xbox 名稱，會嘗試自動選對應 Logo。**缺少 CEC 裝置名稱時不能準確識別，不會僅憑 HDMI 埠猜測**；仍可在手機上手動選圖及改名。

## Android 9–14

原項目 `minSdk=21`、`targetSdk=34`、`compileSdk=36`，可覆蓋 Android 9 API28 至 Android 14 API34。Actions 對 API28／30／34 運行模擬器煙霧測試，其他版本未逐一做真機驗證；尤其 HDMI、背光、Dolby Vision 必須由特定電視及固件支持。

## GitHub Actions / APK

進入 [Aerial 定製 Actions](https://github.com/Kevinleung1212/aerial-tv/actions/workflows/aerial-custom-android9-14.yml)，在成功的 workflow run 頁面底部 **Artifacts** 下載 `Aerial-v1.47-Android9-14-...`。

第一次使用沒有指定金鑰時產出的會是 **PREVIEW-DebugKey**（測試 APK），**每次 GitHub Runner 的 debug 金鑰未必相同，不能依賴直接覆蓋升級**。正式固定簽章請用自己保存的 PKCS12 keystore，並在本 Fork 的 Settings → Secrets and variables → Actions 填入：
- `AERIAL_KEYSTORE_B64`：完整 keystore 檔案 Base64
- `AERIAL_STORE_PASSWORD`：keystore 密碼
- `AERIAL_KEY_ALIAS`：Alias
- `AERIAL_KEY_PASSWORD`：key 密碼

上游包名仍是 `app.orchard.tv`。如電視已安裝另一證書簽署的 Aerial，Android 將拒絕原位更新；先備份 App 私人設定資料，不要直接卸載重要數據。切勿在 GitHub 提交私鑰檔或密碼。

## Windows 10 / Android TV 真機檢查

1. 在電視設定開啟 ADB 開發者選項，Windows 安裝 Google 官方 Platform-Tools。
2. 成功編譯後下載 APK，解壓，從本分支下載 `tools/Test-Aerial-TV.ps1`。
3. PowerShell 在工具檔所在目錄執行：

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\Test-Aerial-TV.ps1 -TvIp 192.168.1.80 -ApkPath .\app-standard-release.apk -Install
```

`192.168.1.80` 只是一個示例，換成你電視實際 LAN IP。也可省略 `-TvIp` 使用 USB ADB。腳本只核對 API 28–34、可選安裝、啟動 Launcher、生成診斷；**不會禁用原生桌面、修改電視系統設定或授權特權**。

手動檢查：玻璃 Dock、全部 App 列表、長按 OK / Menu、文件夾與隱藏、主畫面上鍵→控制中心、HDMI 切換、音量與亮度、手機掃碼拖動排序、粵語 UI、10 秒航拍背景、屏保（4K/DV 能力）、待機喚醒與切換回原生桌面。要驗證 Google TV 9／11／14，需在對應真機上測試，模擬器無法取代。
