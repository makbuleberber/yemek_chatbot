import streamlit as st
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

st.title("🍽️ Akıllı Yemek Öneri Asistanı")

loader = CSVLoader(file_path='yemek_chatbot_veriseti.csv', encoding="utf-8")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(data)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = Chroma.from_documents(documents=docs,embedding=embeddings,persist_directory="./chroma_db")

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs= {"k" : 10})

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    max_tokens=500
)

query=st.chat_input("Say something:")
prompt = query

system_prompt = (
    "You are a helpful assistant specialized in meal recommendations."
    "Use the provided context to answer user questions about recipes and meals."
    "If you don't know the answer, honestly say you don't know."
    "Keep your answers concise, friendly, and limited to three sentences."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        ("human","{input}")
    ]
)

if query:
    question_answer_chain = create_stuff_documents_chain(llm,prompt)
    rag_chain = create_retrieval_chain(retriever,question_answer_chain)
    response = rag_chain.invoke({"input":query})

    st.write(response["answer"])