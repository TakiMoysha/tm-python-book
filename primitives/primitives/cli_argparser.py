import argparse


def grouping_parser():
    parser = argparse.ArgumentParser()

    yellow_group = parser.add_argument_group("yellow")
    yellow_group.add_argument("new_username", type=str)
    yellow_group.add_argument("new_password", type=str)

    green_group = parser.add_argument_group("green")
    green_group.add_argument("old_username", type=str)
    green_group.add_argument("old_password", type=str)

    print(parser.parse_args())


def subparsers():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="types of A")
    parser.add_argument("-v", "--verbose", action="store_true")

    a_parser = subparsers.add_parser("colors")
    a_parser.add_argument("something", choices=["red", "green", "blue"])

    b_parser = subparsers.add_parser("numbers")
    b_parser.add_argument("something", choices=["one", "two", "three"])

    print(parser.parse_args())
