import argparse
import sys
import os

def validate_output_file(file_path: str):
    SUPPORTED_FILE_EXTENSIONS = ['.txt']
    _, file_name = os.path.split(file_path)

    if '.' not in file_name:
        # When no extension is found, a text file format should be assumed.
        return True
    else:
        valid_extension = False
        for extension in SUPPORTED_FILE_EXTENSIONS:
            if file_name.endswith(extension):
                valid_extension = True
        return valid_extension

def create_file(file_path: str, make_dir: bool):
    file_dir, _ = os.path.split(file_path)
    file = None

    if file_dir:
        if os.path.exists(file_dir) or make_dir:
            try:
                os.makedirs(file_dir, exist_ok=True)
                file = open(file_path, 'a')
                return file
            except Exception as e:
                print(f"Encountered an error while trying to create file \"{file_path}\": {str(e)}.")
        else:
            print(f"Error: the path {file_dir} does not exist, and the flag -c was specified.")
    else:
        file = open(file_path, 'a')
        return file


def get_child_pages():
    print ("get child pages called")

def scrape(search_url: str, output_destination:str, recursive:bool, exclude:str):
    print("findLinks was called.")
    print(f"page provided for search was {search_url}")
    print(f"Output Destination: {output_destination}")
    print(f"Recursive: {str(recursive)}")

    exclude_paths = exclude.split()
    if len(exclude_paths) > 0:
        print("Paths excluded from search:")
        for path in exclude_paths:
            print(f"\t- {path}")
    else:
        print("Paths excluded from search: None")

def main():
    parser = argparse.ArgumentParser(description="Crawls a page (or pages) to find broken links.")

    parser.add_argument("source_page", type=str, help="A url to the page you want the script to look for broken links on.")

    parser.add_argument('-f', '--file', type=str, help="(optional) Prints the output to a file instead of the console.")
    parser.add_argument('-c', '--no_new_dirs', action='store_false', help="(optional) The script will not make new directories if the provided one doesn't exist.")
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