@echo off
chcp 65001 > nul
echo ============================================
echo   测试远程知识库
echo ============================================
echo.

ssh root@139.224.207.84 "cd /root/RAG && /root/RAG/venv/bin/python3 << 'PYEOF'
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

from rag.vector_store import VectorStore
from rag.embeddings import BGEEmbeddings

print('初始化知识库...')
vs = VectorStore()
info = vs.get_collection_info()
print(f'✅ 知识库文档数: {info[\"document_count\"]}')
print()

if info['document_count'] > 0:
    print('初始化嵌入模型（带自动训练）...')
    embeddings = BGEEmbeddings(vector_store=vs)
    print()

    print('测试查询: 李木田是谁？')
    results = vs.retrieve('李木田是谁', top_k=3, embeddings_manager=embeddings)

    if results:
        print(f'✅ 检索成功！找到 {len(results)} 个结果:')
        for i, doc in enumerate(results, 1):
            print(f'{i}. 相关度: {doc[\"score\"]:.2%}')
            print(f'   来源: {doc[\"source\"]}')
            print(f'   内容: {doc[\"text\"][:100]}...')
            print()
    else:
        print('❌ 未检索到结果')
else:
    print('❌ 知识库为空')
PYEOF
"

echo.
echo ============================================
echo   测试完成
echo ============================================
pause
