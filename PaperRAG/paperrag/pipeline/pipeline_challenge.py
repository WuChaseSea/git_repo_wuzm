# -*-coding:UTF-8 -*-
'''
* pipeline_challenge.py
* @author wuzm
* created 2025/06/22 22:25:20
* @function: RAG-Challenge-2 Pipeline https://github.com/IlyaRice/RAG-Challenge-2/blob/main/src/pipeline.py#L153
'''
import os, sys
from pathlib import Path
import asyncio, nest_asyncio
from qwen_agent.llm import get_chat_model

from llama_index.core import Settings, PromptTemplate, QueryBundle
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding

from .ingestion import VectorDBIngestor, BM25Ingestor
from ..custom.parser import PDFParser
from ..custom.parsed_reports_merging import PageTextPreparation
from ..custom.text_splitter import TextSplitter
from ..custom.retrievers_challenge import VectorRetriever, BM25Retriever, HybridRetriever
from ..custom.template import QA_TEMPLATE
from ..custom.rerankers import SentenceTransformerRerank, LLMRerank
from .rag import generation as _generation

class PaperRAGChallengePipeline():
    def __init__(self, config):
        self.config = config
        asyncio.get_event_loop().run_until_complete(self.async_init())
    
    async def async_init(self):
        config = self.config
        model_name = config["embedding_name"]
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        bge_embeddings = HuggingFaceBgeEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        self.embedding = bge_embeddings
        Settings.embed_model = self.embedding
        print(f"Embddding 创建完成.")

        self.llm = get_chat_model({
            "model": config["llm_name"],
            "model_server": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": os.getenv("DASHSCOPE_API_KEY"),
        })

        self.qa_template = self.build_prompt_template(QA_TEMPLATE)

        self.parsed_reports_path = Path(self.config["work_dir"]) / Path(self.config["data_path"]).parent / "pdf_parser"
        self.pdf_reports_dir = Path(self.config["work_dir"]) / Path(self.config["data_path"])
        # self.parse_pdf_reports_sequential()
        self.merged_reports_path = Path(self.config["work_dir"]) / Path(self.config["data_path"]).parent / "02_merged_reports"
        # self.merge_reports()
        self.reports_markdown_path = Path(self.config["work_dir"]) / Path(self.config["data_path"]).parent / "03_reports_markdown"
        # self.export_reports_to_markdown()
        self.documents_dir = Path(self.config["work_dir"]) / Path(self.config["data_path"]).parent / "chunked_reports_300"
        # self.chunk_reports()
        self.vector_db_dir = Path(self.config["work_dir"]) / Path(self.config["data_path"]).parent / "vector_dbs"
        # self.create_vector_dbs(embedding_model=self.embedding)
        self.bm25_db_path = Path(self.config["work_dir"]) / Path(self.config["data_path"]).parent / "bm25_dbs"
        # self.create_bm25_db()
        # self.retriever = VectorRetriever(
        #         embedding_model=self.embedding,
        #         vector_db_dir=self.vector_db_dir,
        #         documents_dir=self.documents_dir
        #     )
        self.retriever = HybridRetriever(
            embedding_model=self.embedding,
            vector_db_dir=self.vector_db_dir,
            documents_dir=self.documents_dir,
            llm=self.llm
        )
        # self.retriever = BM25Retriever(
        #     bm25_db_dir=self.bm25_db_path,
        #     documents_dir=self.documents_dir
        # )

    def build_prompt_template(self, qa_template):
        return PromptTemplate(qa_template)
    
    def parse_pdf_reports_sequential(self):
        pdf_parser = PDFParser(
            output_dir=self.parsed_reports_path,
        )
        pdf_parser.parse_and_export(doc_dir=self.pdf_reports_dir)
        print(f"PDF reports parsed and saved to {self.parsed_reports_path}")
    
    def merge_reports(self):
        """Merge complex JSON reports into a simpler structure with a list of pages, where all text blocks are combined into a single string."""
        ptp = PageTextPreparation(use_serialized_tables=False)
        _ = ptp.process_reports(
            reports_dir=self.parsed_reports_path,
            output_dir=self.merged_reports_path
        )
        print(f"Reports saved to {self.merged_reports_path}")
    
    def export_reports_to_markdown(self):
        """Export processed reports to markdown format for review."""
        ptp = PageTextPreparation(use_serialized_tables=False)
        ptp.export_to_markdown(
            reports_dir=self.parsed_reports_path,
            output_dir=self.reports_markdown_path
        )
        print(f"Reports saved to {self.reports_markdown_path}")
    
    def chunk_reports(self, include_serialized_tables: bool = False):
        """Split processed reports into smaller chunks for better processing."""
        text_splitter = TextSplitter()
        
        serialized_tables_dir = None
        if include_serialized_tables:
            serialized_tables_dir = self.parsed_reports_path
        
        text_splitter.split_all_reports(
            self.merged_reports_path,
            self.documents_dir,
            serialized_tables_dir
        )
        print(f"Chunked reports saved to {self.documents_dir}")
    
    def create_vector_dbs(self, embedding_model):
        """Create vector databases from chunked reports."""
        input_dir = self.documents_dir
        output_dir = self.vector_db_dir
        
        vdb_ingestor = VectorDBIngestor(embedding_model=embedding_model)
        vdb_ingestor.process_reports(input_dir, output_dir)
        print(f"Vector databases created in {output_dir}")
    
    def create_bm25_db(self):
        """Create BM25 database from chunked reports."""
        input_dir = self.documents_dir
        output_file = self.bm25_db_path
        
        bm25_ingestor = BM25Ingestor()
        bm25_ingestor.process_reports(input_dir, output_file)
        print(f"BM25 database created at {output_file}")
    
    def _format_retrieval_results(self, retrieval_results) -> str:
        """Format vector retrieval results into RAG context string"""
        if not retrieval_results:
            return ""
        
        context_parts = []
        for result in retrieval_results:
            page_number = result['page']
            text = result['text']
            context_parts.append(f'Text retrieved from page {page_number}: \n"""\n{text}\n"""')
            
        return "\n\n---\n\n".join(context_parts)
    
    def build_query_bundle(self, query_str):
        query_bundle = QueryBundle(query_str=query_str)
        return query_bundle
    
    async def process_quesiton(self, query):
        paper_folder_path = Path(self.config["work_dir"]) / Path(self.config["data_path"]) / query["paper_id"]
        pdfs = [f for f in paper_folder_path.rglob("*.pdf") if not f.name.startswith("._")]
        retrieval_results = self.retriever.retrieve_by_company_name(
            pdfs[0],
            query["question"],
            top_n=4
        )
        if not retrieval_results:
            raise ValueError("No relevant context found")

        rag_context = self._format_retrieval_results(retrieval_results)
        fmt_qa_prompt = self.qa_template.format(
            context_str=rag_context, query_str=query["question"]
        )
        ret = await _generation(self.llm, fmt_qa_prompt)
        return {"answer": ret}
 