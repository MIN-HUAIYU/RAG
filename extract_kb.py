#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取知识库中的所有文档内容"""

import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

import chromadb
import json

# 连接到ChromaDB
client = chromadb.PersistentClient(path='./data/chroma_db')

# 获取所有集合
collections = client.list_collections()
print(f"找到 {len(collections)} 个集合\n")

all_documents = []

for collection in collections:
    print(f"=== 集合: {collection.name} ===")
    col = client.get_collection(name=collection.name)

    # 获取所有文档
    data = col.get(include=['metadatas', 'documents'])

    print(f"文档数: {len(data['ids'])}\n")

    for idx, (doc_id, metadata, document) in enumerate(zip(data['ids'], data['metadatas'], data['documents']), 1):
        source = metadata.get('source', '未知') if metadata else '未知'
        chunk_idx = metadata.get('chunk', 'N/A') if metadata else 'N/A'

        doc_info = {
            'index': idx,
            'id': doc_id,
            'source': source,
            'chunk': chunk_idx,
            'content': document,
            'length': len(document) if document else 0
        }
        all_documents.append(doc_info)

        doc_preview = document[:80] if document else "空"
        print(f"  [{idx}] 来源: {source} (块{chunk_idx})")
        print(f"        长度: {len(document)} 字符")
        print(f"        预览: {doc_preview}...\n")

# 输出为JSON
with open('./knowledge_base_content.json', 'w', encoding='utf-8') as f:
    json.dump(all_documents, f, ensure_ascii=False, indent=2)

print(f"\n总计: {len(all_documents)} 个文档块")
print("已导出到 knowledge_base_content.json")
