import argparse


description = """    
todayi: Keep track of what you do today, and just forget about it.
Writes what you do, everyday, to a backend. Then, retrieve the results
later without having to remember a single thing.
"""


def run():
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("content", help="Description of what you did today.")
    parser.add_argument("-t", default=[])
    print(parser.parse_args().t)


if __name__ == "__main__":
    run()
