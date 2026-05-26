import sys
from pathlib import Path

from vpn_speed_selector.app import create_app


def main() -> int:
    app = create_app(sys.argv)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
