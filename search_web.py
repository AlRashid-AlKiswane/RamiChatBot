from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_transformers import Html2TextTransformer

# Initialize the WebBaseLoader with the target URL
loader = WebBaseLoader("https://www.gig.com.jo/Page/157/%D9%85%D9%86-%D9%86%D8%AD%D9%86")

# Load the documents from the website
docs = loader.load()

# Initialize the HTML to Text transformer
html2text = Html2TextTransformer()

# Transform the loaded HTML documents to plain text
docs_transformed = html2text.transform_documents(docs)

# Access the content of the first transformed document
content = docs_transformed[0].page_content

# Print a snippet of the content
print(content[:1000])  # Prints the first 1000 characters
