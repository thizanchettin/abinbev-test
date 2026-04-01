import argparse

from abinbev_test.bronze.engine import main as bronze_main
from abinbev_test.gold.engine import main as gold_main
from abinbev_test.silver.engine import main as silver_main


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--layer", required=True)

    args = parser.parse_args()

    if args.layer == "bronze":
        bronze_main()
    elif args.layer == "silver":
        silver_main()
    elif args.layer == "gold":
        gold_main()
    else:
        raise ValueError("Invalid layer")


if __name__ == "__main__":
    main()
