import requests as r
import re
import json

header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

cleaned_urls = []
storage = []
urls = []
social_link = []
email = []
def filter_link(social, urls):
    a = [i for i in urls if social in i]
    if a:
        return a[0]
    else:
        return ""

def extract_email(request_text):
    pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+')

    return pattern.findall(request_text)

def check_request(url):
    global invalid_url
    invalid_url = 0
    try:
        request = r.get(url=url)
        print(request.status_code)
        if request.status_code == 200:

            extracted_emails = extract_email(request.text)
            if extracted_emails:
                filtered_emails = append_emails(extracted_emails)
                if filtered_emails:
                    print(f'Found {filtered_emails} in {url}')
            else:
                filtered_emails = ""
            social_link = extract_social_link(request.text)
            if social_link:
                print(f'Found {social_link} in {url}')
            facebook = filter_link('facebook', social_link)
            insta = filter_link('insta', social_link)
            twitter = filter_link('twitter', social_link)
            tiktok = filter_link('tiktok', social_link)
            linkedin = filter_link('linkedin', social_link)
            storage.append({
                        "Url": url,
                        "Email": filtered_emails,
                        "Facebook": facebook,
                        "Instagram": insta,
                        "Tik Tok": tiktok,
                        "Twitter": twitter,
                        "Linkedin": linkedin

                })
            
            return extracted_emails
        else:          
            return None
        
    except r.Timeout:
        print('Request timed out', url)
        invalid_url += 1
        return 't'
    except r.exceptions.SSLError as e:
        print("Invalid url due to SSL Error", url)
        invalid_url += 1
        return 'sll'
    except r.RequestException as e :
        print("Invalid url", url, e)
        invalid_url += 1
        return None

def append_emails(item):
    email_list = []
    if item is not None:
        for i in item:
            if '.png' not in i and '.jpg' not in i and 'example' not in i and '.js' not in i and '.wp' not in i:
                if i not in email_list:
                    email_list.append(i)
                    email.append(i)
    return email_list

def extract_social_link(request_text):
    cleaned_urls = []
    pattern_text = r"https?://(?:www\.)?(facebook\.com/[\w.]+|instagram\.com/[\w.]+|twitter\.com/[\w]+|linkedin\.com/(in|company)/[\w-]+|tiktok\.com/@[\w.]+)"
    matches = re.findall(pattern_text, request_text)
    for match in matches:
        if isinstance(match, tuple):
            url = "https://" + "".join(match)
            print(url)
        else:
            url = match
        if url not in cleaned_urls:
            cleaned_urls.append(url)
            social_link.append(url)
    return cleaned_urls

print('Starting...')
for website in urls:
    for suffix in ["", "/contact", "/contact-us"]:

        url = f"https://{website}{suffix}"
        emails = check_request(url)
        if emails == 'sll':
            break
        if emails == 't':
            break


with open('data.json', 'w') as file:
    json.dump(storage, file)

import csv


flattened_data = []
for item in storage:
    for url, details in item.items():
        flattened_details = {'url': url}
        flattened_details.update(details)
        flattened_data.append(flattened_details)


with open('data.csv', 'w', newline='') as csv_file:
    fieldnames = ['url', 'email', 'Facebook', 'Instagram', 'Tik Tok', 'Twitter', 'Linkedin']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in flattened_data:
        writer.writerow(row)
