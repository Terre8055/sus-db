import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Initialize the Slack client
client = WebClient(token=os.getenv("SLACK_TOKEN"))

# Upload a file to Slack
def upload_file(file_path):
    try:
        with open(file_path, "rb") as file:
            response = client.files_upload(
                channels=os.getenv("SLACK_CHANNEL"),
                file=file,
                initial_comment="Here is the Trivy report file"
            )
            print(response)
        print("File uploaded successfully to Slack!")
    except SlackApiError as e:
        print(f"Error uploading file to Slack: {e.response['error']}")

# Use the GitHub environment variable to get the timestamp
timestamp = os.getenv("TIMESTAMP")

# Upload the Trivy report file to Slack
upload_file(f"trivy_report_{timestamp}.json")
