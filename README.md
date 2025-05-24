[![Built with](https://img.shields.io/badge/Built%20with-Stima%20API-blueviolet?logo=robot)](https://api.stima.tech)
# YouTube 音樂下載器

這是一個簡單易用的網頁應用程式，可以從YouTube下載單一影片或播放清單，並轉換為MP3格式。

## 功能特色

- 支援單一YouTube影片下載
- 支援YouTube播放清單批次下載
- 自動轉換為高品質MP3格式
- 即時顯示下載進度
- 自動添加ID3標籤和專輯封面
- 支援Docker容器化部署

## 技術架構

- **後端框架**：Flask 3.0.3
- **YouTube下載引擎**：yt-dlp 2025.01.15
- **音訊處理**：mutagen 1.47.0
- **容器化**：Docker
- **其他工具**：
  - FFmpeg (自動下載安裝)
  - fake_useragent 2.0.3 (防止API封鎖)


## 安裝與執行

### 使用Docker (推薦)

1. 建立Docker映像檔：
