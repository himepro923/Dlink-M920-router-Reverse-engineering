import time
import serial
from pathlib import Path

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 38400
BINARY_FILE = "snake"

CHUNK_SIZE = 128
DELAY = 0.12

data = Path(BINARY_FILE).read_bytes()

print(f"File size: {len(data)} bytes")
print(f"Opening {SERIAL_PORT} at {BAUD_RATE} baud...")

with serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=1,
    write_timeout=5
) as ser:

    time.sleep(1)

    # Clear the destination file.
    ser.write(b": > /tmp/snake\n")
    ser.flush()
    time.sleep(1)

    total = (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE

    for number, start in enumerate(range(0, len(data), CHUNK_SIZE), 1):
        chunk = data[start:start + CHUNK_SIZE]

        escapes = "".join(
            f"\\x{byte:02x}" for byte in chunk
        )

        command = f"printf '{escapes}' >> /tmp/snake\n"

        ser.write(command.encode("ascii"))
        ser.flush()

        time.sleep(DELAY)

        if number % 25 == 0 or number == total:
            progress = start + len(chunk)
            print(
                f"\rProgress: {progress}/{len(data)} bytes "
                f"({progress / len(data) * 100:.1f}%)",
                end="",
                flush=True
            )

    print("\nTransfer commands completed.")
    time.sleep(2)
