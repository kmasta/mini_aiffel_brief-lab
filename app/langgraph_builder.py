# app/langgraph_builder.py
from langgraph.graph import StateGraph, END
from langchain.schema.runnable import RunnableLambda
from modules.retriever import vector_retriever
#from modules.merger import group_by_article
from modules.summarizer import chunk_summarizer_node #, article_summarizer_node
from modules.formatter import format_email_node


def build_pipeline():
    # 초기 입력 및 최종 출력 키 설정
    g = StateGraph(
        input=("user_id", "keywords", "email"),
        output=("user_id", "mail")
    )

    # 에이전트(노드) 정의
    g.add_node('retrieve', RunnableLambda(vector_retriever))
    #g.add_node('merge', RunnableLambda(group_by_article)) TODO
    g.add_node('chunk_sum', RunnableLambda(chunk_summarizer_node))
    #g.add_node('art_sum', RunnableLambda(article_summarizer_node))
    g.add_node('format', RunnableLambda(format_email_node))

    # 흐름 연결
    g.set_entry_point('retrieve')
    g.add_edge('retrieve', 'chunk_sum')
    #g.add_edge('merge', 'chunk_sum')
   # g.add_edge('chunk_sum', 'art_sum')
    g.add_edge('chunk_sum', 'format')
    g.add_edge('format', END)

    return g.compile()
