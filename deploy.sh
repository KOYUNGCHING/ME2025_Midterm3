#!/bin/bash
set -e  # 有錯就中止腳本，避免跑到一半壞掉還繼續
REPO_URL="https://github.com/KOYUNGCHING/ME2025_Midterm3.git"

# 專案要放在哪個資料夾
TARGET_DIR="$HOME/ME2025_Midterm3"

# 首次執行：如果資料夾不存在 → git clone
# 第二次以後：如果資料夾已存在 → git pull

if [ -d "$TARGET_DIR/.git" ]; then
    echo "=== 第二次以後執行：更新專案 ==="
    cd "$TARGET_DIR"
    git pull
else
    echo "=== 第一次執行：clone 專案 ==="
    git clone "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

# 建立或使用 .venv 虛擬環境

if [ ! -d ".venv" ]; then
    echo "建立 .venv 虛擬環境..."
    python3 -m venv .venv
fi

# 啟用虛擬環境
source .venv/bin/activate

# 安裝 / 更新 requirements.txt 中的套件
# （pip install -r 本來就會自動安裝缺的、略過已裝好的）
if [ -f "requirements.txt" ]; then
    echo "安裝 / 更新 requirements.txt 套件..."
    pip install -r requirements.txt
else
    echo "⚠️ 找不到 requirements.txt，略過安裝步驟。"
fi

# 重啟 app.py
#   先把舊的 python3 app.py 關掉，再啟動新的
echo "檢查是否有舊的 app.py 在執行..."
OLD_PIDS=$(ps aux | grep "python3 app.py" | grep -v grep | awk '{print $2}')

if [ -n "$OLD_PIDS" ]; then
    echo "找到舊的 app.py (PID: $OLD_PIDS)，正在停止..."
    kill $OLD_PIDS
    sleep 1
fi

echo "啟動 app.py ..."
python3 app.py