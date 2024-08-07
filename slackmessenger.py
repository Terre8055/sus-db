import os
from slack_url import shorten
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging


logging.basicConfig(level=logging.DEBUG)
# Initialize the Slack client
client = WebClient(token=os.environ["SLACK_TOKEN"])
timestamp = os.environ["TIMESTAMP"]
presigned_url = os.environ["PRESIGNED_URL"]
file_path = f"trivy_report_table_{timestamp}.txt"


shorten_presign_url = shorten(presigned_url)
try:
    with open(file_path, "r") as file:
        file_content = file.read()

    new_file = client.files_upload_v2(
        title="Trivy Report",
        filename=file_path,
        content=file_content,
    )
    file_url = new_file.get("file").get("permalink")
    
    new_message = client.chat_postMessage(
        channel="C076CEFAXJ5",
        text=f"Here is the file: {file_url} and the detailed report can be accessed at: {shorten_presign_url}. Valid for 10 hours",
    )
    print("File uploaded and message sent successfully!")
except FileNotFoundError:
    print(f"Error: File {file_path} not found.")
except SlackApiError as e:
    print(f"Error uploading file or sending message to Slack: {e.response['error']}")

