
import requests

def shorten(url):
    api_url = "http://tinyurl.com/api-create.php"
    params = {'url': url}
    try:
        response = requests.get(api_url, params=params, timeout=240)  # 2 minutes timeout
        response.raise_for_status()
        short_url = response.text
        print(short_url)
    except requests.exceptions.ReadTimeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    shorten(url)


