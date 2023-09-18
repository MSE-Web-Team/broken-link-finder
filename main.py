import argparse
import sys
import os
import requests

"""
Validates the user's provided output file path. Returns true or false.
"""
def validate_output_file(file_path: str):
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
def create_file(file_path: str):
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
Gets a list of pages within the domain that are linked on a page.
"""
def get_child_pages(search_url, base_url):
    print(f"get child pages called: {search_url}, {base_url}")

"""
Gets all values in href properties from anchor tags.
"""
def get_anchor_refs(search_url):
    print(f"get_anchor_refs called: {search_url}")

"""
Separates a https://<domain> from an endpoint in a url.
"""
def url_separate(url):
    parsed_url = requests.utils.urlparse(url)
    scheme = parsed_url.scheme
    domain = parsed_url.netloc
    endpoint = parsed_url.path

    base_url = f"{scheme}{domain}"

    return base_url, endpoint

"""
Hub function for scraping the page/site provided. Should output to a file or console (depending
on the arguments provided) one line at a time when broken links are found.
"""
def scrape(search_url: str, output_destination:str, recursive:bool, exclude:str):
    exclude_paths = exclude.split()
    if len(exclude_paths) > 0:
        print("Paths excluded from search:")
        for path in exclude_paths:
            print(f"\t- {path}")
    else:
        print("Paths excluded from search: None")

    if output_destination != "console":
        valid_out_dest = validate_output_file(output_destination)
        output_file = create_file(output_destination)
        DOMAIN,start_endpoint = url_separate(search_url)

        
    else:
        print("Console output not implemented yet")

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

    output_dest = "console"
    exclude_paths = ""
    if args.file:
        output_dest = args.file
    if args.exclude:
        exclude_paths = args.exclude

    scrape(args.source_page, output_dest, args.recursive, exclude_paths)

if __name__ == "__main__":
    main()