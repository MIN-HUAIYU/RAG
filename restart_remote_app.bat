@echo off
chcp 65001 > nul
echo ============================================
echo   重启远程 Streamlit 应用
echo ============================================
echo.

echo [步骤 1/4] 停止旧的 Streamlit 进程...
ssh root@139.224.207.84 "pkill -f 'streamlit run'"
timeout /t 3 /nobreak > nul
echo   完成
echo.

echo [步骤 2/4] 清理旧日志...
ssh root@139.224.207.84 "rm -f /tmp/streamlit_restart.log"
echo   完成
echo.

echo [步骤 3/4] 启动新的 Streamlit 应用（已修复 TF-IDF 问题）...
ssh root@139.224.207.84 "cd /root/RAG && export PYTHONPATH=/root/RAG && nohup /root/RAG/venv/bin/streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0 > /tmp/streamlit_restart.log 2>&1 &"
echo   已启动后台进程
echo.

echo [步骤 4/4] 等待应用启动完成（15秒）...
timeout /t 15 /nobreak
echo.

echo ============================================
echo   查看启动日志
echo ============================================
ssh root@139.224.207.84 "tail -100 /tmp/streamlit_restart.log"
echo.

echo ============================================
echo   检查关键信息
echo ============================================
echo.
echo 查找 TF-IDF 训练日志：
ssh root@139.224.207.84 "grep -i 'TF-IDF' /tmp/streamlit_restart.log | tail -10"
echo.

echo 查找文档数量：
ssh root@139.224.207.84 "grep -i 'documents:' /tmp/streamlit_restart.log | tail -5"
echo.

echo ============================================
echo   部署完成！
echo ============================================
echo.
echo 网页地址: http://139.224.207.84:8501
echo.
echo 如果看到 "✅ TF-IDF 模型训练完成" 说明修复成功！
echo 现在可以在网页上提问测试知识库了。
echo.
pause
