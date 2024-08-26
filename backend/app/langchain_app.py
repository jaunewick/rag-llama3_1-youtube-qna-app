import os
from dotenv import load_dotenv

# OpenAI imports
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

# Ollama imports
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings

# Langchain imports
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Pinecone imports
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore

# Youtube transcriber imports
import tempfile
from pytubefix import YouTube
import whisper

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MODEL = "gpt-3.5-turbo"
MODEL = "llama3.1"

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = "ytb-index"

# Sam Altman: OpenAI CEO on GPT-4, ChatGPT, and the Future of AI
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=L_Guz73e6fw"

# Setting up llm/slm model with its corresponding embeddings
if MODEL.startswith("gpt"):
    model = ChatOpenAI(api_key=OPENAI_API_KEY,model=MODEL)
    embeddings = OpenAIEmbeddings()
    DIMENSIONS = 1536
else:
    model = Ollama(model=MODEL)
    embeddings = OllamaEmbeddings(model=MODEL)
    DIMENSIONS = 4096

## Setting up the prompt templates
template = """
Answer the question based on the context below.
If you can't answer the question, reply "I don't know"

Context: {context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

def store_into_pinecone(video_url):
    # Transcribing YouTube Video
    if not os.path.exists("ytb_transcript.txt"):
        youtube = YouTube(video_url)
        audio = youtube.streams.filter(only_audio=True).first()

        # "base" model used for ok accuracy and fast transcribing
        whisper_model = whisper.load_model("base")

        with tempfile.TemporaryDirectory() as tmpdir:
            file = audio.download(output_path=tmpdir)
            transcription = whisper_model.transcribe(file, fp16=False)["text"].strip()

            with open("ytb_transcript.txt", "w") as file:
                file.write(transcription)

    # Splitting into documents
    loader = TextLoader("ytb_transcript.txt")
    txt_documents = loader.load()
    txt_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    documents = txt_splitter.split_documents(txt_documents)

    # Loading into the Pinecone vector store
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSIONS,
            metric='cosine',
            spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
            )
        )
        PineconeVectorStore.from_documents(documents, embeddings, index_name=INDEX_NAME)

def delete_index_pinecone():
    if INDEX_NAME in pc.list_indexes().names():
        pc.delete_index(INDEX_NAME)

def answer_question(question):
    pinecone = PineconeVectorStore(embedding=embeddings, index_name=INDEX_NAME)
    retriever = pinecone.as_retriever()
    setup = RunnableParallel(context=retriever, question=RunnablePassthrough())
    parser = StrOutputParser()
    chain = setup | prompt | model | parser
    answer = chain.invoke(question)
    return answer