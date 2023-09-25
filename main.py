import argparse
import sys
import os
import requests
import io

# Selenium imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# BeautifulSoup
from bs4 import BeautifulSoup

"""
Validates the user's provided output file path. Returns true or false.
"""
def validate_output_file(file_path: str) -> bool:
    SUPPORTED_FILE_EXTENSIONS = ['.txt']
    file_dir, file_name = os.path.split(file_path)

    if '.' not in file_name:
        # When no extension is found, a text file format should be assumed.
        return True
    else:
        valid_file = True
        valid_extension = False
        for extension in SUPPORTED_FILE_EXTENSIONS:
            if file_name.endswith(extension):
                valid_extension = True
        if not os.access(file_dir, os.W_OK):
            print(f"Improper permission to write in the directory {file_dir}.")
            valid_file = False
        if not valid_extension:
            print(f"The extension {file_name.split('.')[1]} is not supported")
            valid_file = False
        return valid_file

"""
Performs necessary checks to see if a file with the provided path can be created.
returns the result of an open(<path>, "a") if checks are successful.
"""
def create_file(file_path: str) -> io.IOBase:
    file_dir, _ = os.path.split(file_path)
    file = None

    path_exists = os.path.exists(file_dir)
    if file_dir and path_exists:
        try:
            os.makedirs(file_dir, exist_ok=True)
            file = open(file_path, 'a')
            return file
        except Exception as e:
            print(f"Encountered an error while trying to create file \"{file_path}\": {str(e)}.")
            sys.exit()
    elif not file_dir:
        print("No path was provided to create_file")
        sys.exit()
    elif not path_exists:
        print(f"Error: the path {file_dir} does not exist")
        sys.exit()
    else:
        return open(file_path, 'a')

"""
Finds links on a page that are in the sub-domain of the url provided and returns any that are not
already searched.
"""
def get_child_pages(search_url: str, searched: list) -> list:
    print(f"get child pages called: {search_url} {searched}")

"""
Looks for broken links on a page. Returns an array of broken links when finished.
"""
def test_links(url: str) -> list:
    print(f"test_links called: {url}")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    anchor_tags = soup.find_all('a')
    href_count = 0
    broken_count = 0
    for anchor in anchor_tags:
        href = anchor.get('href')
        if href is None:
            continue
        response = requests.head(href)
        if response.status_code != 200:
            print(f'Broken link: {href} (Status code: {response.status_code})')
            broken_count += 1
        href_count += 1
    driver.close()
    print(f'Looked at {href_count} links and found {broken_count} broken')

"""
Separates a https://<domain> from an endpoint in a url.
"""
def url_separate(url: str) -> tuple:
    parsed_url = requests.utils.urlparse(url)
    scheme = parsed_url.scheme
    domain = parsed_url.netloc
    endpoint = parsed_url.path

    base_url = f"{scheme}{domain}"

    return base_url, endpoint

"""
Finds all broken links on a page.
"""
def find_broken_links(start_url: str, recursive: bool, output_file: io.IOBase = None) -> None:
    START_DOMAIN, start_endpoint = url_separate(start_url)
    url_queue = []
    url_queue.append(start_endpoint)
    searched_urls = []
    broken_refs = []

    while len(url_queue) > 0:
        broken_refs += test_links(f"{START_DOMAIN}{url_queue[0]}")
        if recursive:
            url_queue += get_child_pages(f"{START_DOMAIN}{url_queue[0]}", searched_urls)
        url_queue.pop(0)

        if output_file != None:
            for link in broken_refs:
                output_file.write(link)
        else:
            for link in broken_refs:
                print(link)
        broken_refs = []

"""
Hub function for scraping the page/site provided. Should output to a file or console (depending
on the arguments provided) one line at a time when broken links are found.
"""
def scrape(search_url: str, recursive: bool, exclude: str, output_destination: str = "console"):
    exclude_paths = exclude.split()
    if len(exclude_paths) > 0:
        print("Paths excluded from search:")
        for path in exclude_paths:
            print(f"\t- {path}")
    else:
        print("Paths excluded from search: None")

    if output_destination != "console":
        # Check to see if the path provided is a valid file path.
        valid_out_dest = validate_output_file(output_destination)
        if valid_out_dest:
            # Print to file destination if it is.
            output_file = create_file(output_destination)
            find_broken_links(search_url, recursive, output_file)
            output_file.close()
        else:
            # The output destination is invalid otherwise
            response = ''
            while response.lower() != 'y' or response.lower() != 'n':
                # Check if the user wants to print to console instead.
                response = input(f"The destination {output_destination} is not valid. Do you want to print to the console instead? (y/n)")
            if response == 'n':
                # Stop if they say no
                print("Stopping execution")
                sys.exit()
            else:
                # print to console if yes.
                find_broken_links(search_url, recursive)
    else:
        # A file destination was not provided. Print results to console.
        find_broken_links(search_url, recursive)

def main():
    parser = argparse.ArgumentParser(description="Crawls a page (or pages) to find broken links.")

    # positional arguments
    parser.add_argument("source_page", type=str, help="A url to the page you want the script to look for broken links on.")
    # optional arguments
    parser.add_argument('-f', '--file', type=str, help="(optional) Prints the output to a file instead of the console.")
    parser.add_argument('-r', '--recursive', action='store_true', help="(optional) Causes the script to search all linked pages within the same domain (won't go out of current sub-domain)")
    parser.add_argument('-x', '--exclude', type=str, help="(optional) Paths to exclude when searching other pages. No effect unless -r is specified")

    args = None
    try:
        args = parser.parse_args()
    except SystemExit:
        parser.print_help()
        sys.exit()
    exclude_paths = ""
    output_dest = args.file
    if args.exclude:
        exclude_paths = args.exclude

    if output_dest:
        scrape(args.source_page, args.recursive, exclude_paths, output_dest)
    else: scrape(args.source_page, args.recursive, exclude_paths)

if __name__ == "__main__":
    main()