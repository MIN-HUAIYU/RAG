@echo off
echo Deploying fix to remote server...
echo.

echo [1/5] Uploading rag/embeddings.py...
scp "rag\embeddings.py" root@139.224.207.84:/root/RAG/rag/
if %ERRORLEVEL% NEQ 0 (echo Failed! & exit /b 1)

echo [2/5] Uploading app/main.py...
scp "app\main.py" root@139.224.207.84:/root/RAG/app/
if %ERRORLEVEL% NEQ 0 (echo Failed! & exit /b 1)

echo [3/5] Stopping old Streamlit process...
ssh root@139.224.207.84 "pkill -f 'streamlit run'"

echo [4/5] Waiting 3 seconds...
timeout /t 3 /nobreak > nul

echo [5/5] Starting Streamlit with fixed code...
ssh root@139.224.207.84 "cd /root/RAG && export PYTHONPATH=/root/RAG:$PYTHONPATH && nohup /root/RAG/venv/bin/streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0 > /tmp/streamlit.log 2>&1 &"

echo.
echo Waiting 8 seconds for startup...
timeout /t 8 /nobreak > nul

echo.
echo === Checking logs ===
ssh root@139.224.207.84 "tail -80 /tmp/streamlit.log"

echo.
echo === Deployment complete! ===
echo Open: http://139.224.207.84:8501
