from langchain_community.vectorstores import SurrealDBStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomSurrealDBStore(SurrealDBStore):
    async def aadd_texts(self, texts, metadatas=None, **kwargs):
        logger.info(f"aadd_texts called with texts: {texts}, metadatas: {metadatas}")
        try:
            result = await super().aadd_texts(texts, metadatas, **kwargs)
            logger.info(f"aadd_texts result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in aadd_texts: {type(e).__name__}, {str(e)}")
            raise