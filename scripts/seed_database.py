import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from scripts.seed_demo import main as seed_demo

    print("Legacy bulk mock seed is retired; using the guarded single-resident demo command.", file=sys.stderr)
    seed_demo()


if __name__ == "__main__":
    main()
