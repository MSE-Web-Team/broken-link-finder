import argparse
import sys

def find_links(search_url: str, output_destination:str, recursive:bool, exclude:str):
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
    parser.add_argument('-r', '--recursive', action='store_true', help="(optional) Causes the script to search all linked pages within the same domain (won't go out of current sub-domain)")
    parser.add_argument('-x', '--exclude', type=str, help="(optional) Paths to exclude when searching other pages. No effect unless -r is specified")

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

    find_links(args.source_page, output_dest, args.recursive, exclude_paths)


if __name__ == "__main__":
    main()


def get_child_pages():
    print ("get child pages called")