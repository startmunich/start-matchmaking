from langchain_community.vectorstores import SurrealDBStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomSurrealDBStore(SurrealDBStore):
    async def aadd_texts(self, texts, metadatas=None, **kwargs):
        logger.info(f"aadd_texts called with texts: {texts}, metadatas: {metadatas}")
        try:
            embeddings = self.embedding_function.embed_documents(list(texts))
            ids = []
            for idx, text in enumerate(texts):
                data = {"text": text, "embedding": embeddings[idx]}
                if metadatas is not None and idx < len(metadatas):
                    data["metadata"] = metadatas[idx]
                else:
                    data["metadata"] = []
                record = await self.sdb.create(
                    self.collection,
                    data,
                )
                logger.info(f"Record created: {record}")
                if isinstance(record, list) and len(record) > 0 and isinstance(record[0], dict):
                    ids.append(record[0].get("id", str(record[0])))
                elif isinstance(record, dict):
                    ids.append(record.get("id", str(record)))
                else:
                    ids.append(str(record))
            logger.info(f"aadd_texts result: {ids}")
            return ids
        except Exception as e:
            logger.error(f"Error in aadd_texts: {type(e).__name__}, {str(e)}")
            raise