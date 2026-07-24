import logging
import os
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import azure.durable_functions as df
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import requests
from datetime import datetime

my_app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

_openai_credential = DefaultAzureCredential()

def _build_storage_credential():
    # In Azure, prefer explicit UAMI to avoid credential-chain ambiguity.
    if os.environ.get("IDENTITY_ENDPOINT") or os.environ.get("MSI_ENDPOINT"):
        return ManagedIdentityCredential(client_id=os.environ.get("AZURE_CLIENT_ID"))
    return DefaultAzureCredential()

def _build_blob_service_client():
    jobs_storage = os.environ.get("AzureWebJobsStorage", "")
    if "UseDevelopmentStorage=true" in jobs_storage or "127.0.0.1" in jobs_storage or "localhost" in jobs_storage:
        return BlobServiceClient.from_connection_string(jobs_storage)

    credential = _build_storage_credential()
    storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
    if not storage_account_name:
        raise ValueError("STORAGE_ACCOUNT_NAME environment variable is required but not set")

    return BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=credential
    )


def _summarize_with_azure_openai(text: str):
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    deployment = os.environ.get("CHAT_MODEL_DEPLOYMENT_NAME", "")

    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required but not set")
    if not deployment:
        raise ValueError("CHAT_MODEL_DEPLOYMENT_NAME environment variable is required but not set")

    api_key = os.environ.get("AZURE_OPENAI_KEY")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if api_key:
        headers["api-key"] = api_key
    else:
        token = _openai_credential.get_token("https://cognitiveservices.azure.com/.default").token
        headers["Authorization"] = f"Bearer {token}"

    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-10-21"
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You summarize documents concisely and clearly.",
            },
            {
                "role": "user",
                "content": f"Can you explain what the following text is about? {text}",
            },
        ],
        "temperature": 0.2,
        "max_tokens": 1000,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=90)
    if response.status_code >= 400:
        logging.error("Azure OpenAI call failed with status %s: %s", response.status_code, response.text[:1000])
        response.raise_for_status()

    response_json = response.json()
    content = response_json["choices"][0]["message"]["content"]
    return {"content": content}

blob_service_client = _build_blob_service_client()

@my_app.blob_trigger(arg_name="myblob", path="input", connection="AzureWebJobsStorage")
@my_app.durable_client_input(client_name="client")
async def blob_trigger(myblob: func.InputStream, client):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name} "
                f"Blob Size: {myblob.length} bytes")

    blobName = myblob.name.split("/")[1]
    await client.start_new("process_document", client_input=blobName)

# Orchestrator
@my_app.orchestration_trigger(context_name="context")
def process_document(context):
    blobName: str = context.get_input()

    first_retry_interval_in_milliseconds = 5000
    max_number_of_attempts = 3
    retry_options = df.RetryOptions(first_retry_interval_in_milliseconds, max_number_of_attempts)

    # Download the PDF from Blob Storage and use Document Intelligence Form Recognizer to analyze its contents.
    result = yield context.call_activity_with_retry("analyze_pdf", retry_options, blobName)
    # Send the analyzed contents to Azure OpenAI to generate a summary.
    result2 = yield context.call_activity_with_retry("summarize_text",  retry_options, result)
    # Save the summary to a new file and upload it back to storage.
    result3 = yield context.call_activity_with_retry("write_doc", retry_options, { "blobName": blobName, "summary": result2 })

    return logging.info(f"Successfully uploaded summary to {result3}")

@my_app.activity_trigger(input_name='blobName')
def analyze_pdf(blobName):
    logging.info(f"in analyze_text activity")
    global blob_service_client
    container_client = blob_service_client.get_container_client("input")
    blob_client = container_client.get_blob_client(blobName)
    blob =  blob_client.download_blob().read()
    doc = ''

    endpoint = os.environ["COGNITIVE_SERVICES_ENDPOINT"]
    credential = DefaultAzureCredential()

    document_analysis_client = DocumentAnalysisClient(endpoint, credential)

    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document=blob, locale="en-US")
    result = poller.result().pages

    for page in result:
        for line in page.lines:
            doc += line.content

    return doc

# we removed the binding because it doesn't work with default azure authentication. 
# Instead, we will use a custom function to leverage the DefaultAzureCredential to get a token and pass it in the header.
@my_app.activity_trigger(input_name='results')
def summarize_text(results):
    logging.info(f"in summarize_text activity")
    response_json = _summarize_with_azure_openai(results)
    logging.info(response_json["content"])
    return response_json

@my_app.activity_trigger(input_name='results')
def write_doc(results):
    logging.info(f"in write_doc activity")
    global blob_service_client
    container_client=blob_service_client.get_container_client("output")

    summary = results['blobName'] + "-" + str(datetime.now())
    sanitizedSummary = summary.replace(".", "-")
    fileName = sanitizedSummary + ".txt"

    logging.info("uploading to blob" + results['summary']['content'])
    container_client.upload_blob(name=fileName, data=results['summary']['content'])
    return str(summary + ".txt")
