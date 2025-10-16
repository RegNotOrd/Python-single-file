#!/usr/bin/env python3
"""
auto_clicker.py

Continuously left-clicks at the given screen coordinates.

Usage examples:
  # default: click (422, 534) every 5 seconds indefinitely
  python auto_clicker.py

  # specify coords, interval (seconds) and count
  python auto_clicker.py --x 422 --y 534 --interval 5

  # click N times then stop
  python auto_clicker.py --count 10

Notes:
- To stop: press Ctrl+C in the terminal.
- The script will move the real mouse and click — make sure this is safe for your system.
- For your screen resolution (1920x1680) the coordinate (422,534) is well inside the screen.
"""
import time
import argparse
from pynput.mouse import Controller, Button

def main():
    p = argparse.ArgumentParser(description="Auto clicker - left click at coordinates repeatedly.")
    p.add_argument("--x", type=int, default=352, help="X coordinate (default 422)")
    p.add_argument("--y", type=int, default=434, help="Y coordinate (default 534)")
    p.add_argument("--interval", type=float, default=5.0, help="Seconds between clicks (default 5.0)")
    p.add_argument("--count", type=int, default=0, help="Number of clicks (0 => infinite).")
    p.add_argument("--move-first", action="store_true", help="Move the mouse to target before starting (default True).")
    args = p.parse_args()

    mouse = Controller()
    x = args.x
    y = args.y
    interval = args.interval
    count = args.count

    print(f"Auto clicker starting. Clicking at ({x}, {y}) every {interval} seconds.")
    if count:
        print(f"Will click {count} times then exit.")
    else:
        print("Will click indefinitely. Press Ctrl+C to stop.")

    try:
        if args.move_first:
            try:
                mouse.position = (x, y)
            except Exception:
                pass

        i = 0
        while True:
            if count and i >= count:
                break
            try:
                # move to coordinate (keeps cursor visible)
                mouse.position = (x, y)
                # perform left click (press + release)
                mouse.press(Button.left)
                mouse.release(Button.left)
                i += 1
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{ts}] Click #{i} at ({x}, {y})")
            except Exception as e:
                print("Click failed:", e)

            # sleep between clicks
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C). Exiting.")
    except Exception as e:
        print("Unexpected error:", e)
    finally:
        print("Auto clicker stopped.")

if __name__ == "__main__":
    main()
