from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import JsonOutputParser
from langchain_milvus import Milvus
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader


class ResumeData(BaseModel):
    name: str = Field("name of the user")
    email: str = Field("email of the user")
    phone: str = Field("phone number of the user")
    education: str = Field("education details of the user")
    work_experience: str = Field("work experience of the user")
    skills: str = Field("skill set of the user")


def get_content_from_llm(file_path: str):
    # load the resume
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # initalize Milvus vectorstore with OpenAI embeddings
    vectorstore = Milvus.from_documents(
        documents=splits,
        embedding=OpenAIEmbeddings(),
    )
    retriever = vectorstore.as_retriever()

    # use gpt-4o-mini model
    llm = ChatOpenAI(model="gpt-4o-mini")

    # define the output parser for ResumeData
    output_parser = JsonOutputParser(pydantic_object=ResumeData)

    # define the prompt template for extracting information
    template = """
        You are an AI assistant designed to extract information from resumes.
        Given the following resume content, please extract the relevant information and format it according to the specified JSON structure.

        Resume content:
        {context}

        Please extract the following information:
        - Name
        - Email
        - Phone number
        - Education details
        - Work experience
        - Skills

        NOTE:
            - for the work experience - fetch all of them and extract only the timeframe, the organization and the role/position.
            - if there are multiple education details or work experience put them into a list.

        Format the extracted information in the following JSON structure:
        {format_instructions}

        If any field is not found in the resume, use "Not Provided" as the value
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["context"],
        partial_variables={
            "format_instructions": output_parser.get_format_instructions()
        },
    )

    chain = {"context": retriever} | prompt | llm | output_parser

    response = chain.invoke(input="extract the contents from the given resume")
    return response


def parse_resume_llm(file_path: str):
    response = get_content_from_llm(file_path)

    return response
