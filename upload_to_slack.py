import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def upload_file_to_slack(token, channel, filename, title):
    client = WebClient(token=token)

    try:
        response = client.files_upload(
            channels=channel,
            file=filename,
            filename=title,
            initial_comment="Uploading Trivy Report to Slack",
        )
        print(response)

    except SlackApiError as e:
        print(f"Error uploading file to Slack: {e.response['error']}")

def main():
    slack_token = os.environ.get("SLACK_TOKEN")
    slack_channel = os.environ.get("SLACK_CHANNEL")
    timestamp = os.environ.get("TIMESTAMP")

    filename = f"trivy_report_{timestamp}.json"
    title = f"Trivy Report {timestamp}"

    upload_file_to_slack(slack_token, slack_channel, filename, title)

if __name__ == "__main__":
    main()

