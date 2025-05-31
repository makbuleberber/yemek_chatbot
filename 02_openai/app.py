import streamlit as st
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv

load_dotenv()

st.title("🍽️ Akıllı Yemek Öneri Asistanı")

# 1. Veri yükleme
loader = CSVLoader(file_path="yemek_chatbot_veriseti.csv", encoding="utf-8")
data = loader.load()

# 2. Böl ve vektörle
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(data)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    max_tokens=500
)

# 3. Sorgu yapısı
query = st.chat_input("Canın ne çekiyor? 🍲 Tarif, öneri ya da atıştırmalık sorabilirsin!")

system_prompt = (
    "Sen, yemek önerileri sunan cana yakın bir dijital asistansın. "
    "Kullanıcıdan gelen mesajlara kısa, samimi ve eğlenceli yanıtlar ver. "
    "Yalnızca yemekler, tarifler ve malzeme önerileri hakkında konuş. Başka konulara girme. "
    "Yanıtlarını Türkçe 🇹🇷 yaz ve emojilerle 📌 zenginleştir. "
    "Kısa paragraflar ya da 2–3 cümle yeterlidir."
    "\n\n"
    "{context}"
)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}")
    ]
)

if query:
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    response = rag_chain.invoke({"input": query})

    st.write(response["answer"])
