from langchain_community.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import warnings
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from llm.base_model import LanguageModel
warnings.filterwarnings("ignore")
class RAG:
    def __init__(self):
        self.documents = []
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.embeddings = HuggingFaceEmbeddings()
        self.db = None  # 延迟初始化
        self.qa = None
        self.llm = LanguageModel().get_llm()
        
        # 定义prompt模板
        self.prompt_template = PromptTemplate.from_template(
            """请用中文回答，并遵循以下规则：
            上下文：{context}
            问题：{question}
            要求：
            1. 答案不超过50字
            2. 如果不知道就说"无法回答"

            答案："""
        )

    def load_document(self, file):
        """加载并索引文档"""
        loader = PDFPlumberLoader(file)
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        
        if not chunks:
            raise ValueError("文档分割后未得到有效文本块")
        # 首次加载时初始化FAISS
        if self.db is None:
            self.db = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.db.add_documents(chunks)
        
        self._init_qa_chain()

    def _init_qa_chain(self):
        """初始化QA链"""
        if not self.db:
            raise ValueError("请先加载文档")
        # 现在 self.llm 已经是符合 LangChain 要求的 LLM 对象
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.db.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )

    def retrieve_and_generate(self, query):
        """检索并生成答案"""
        if not self.qa:
            raise ValueError("请先调用load_document()加载文档")
        return self.qa.invoke({"query": query})["result"]

if __name__ == "__main__":
    rag = RAG()
    print("正在构建知识库...")
    rag.load_document("D:\\learn_AI\\small_agent\\rag\\南瓜书.pdf")
    result = rag.retrieve_and_generate("南瓜书的作者是谁？")
    print("答案:", result)