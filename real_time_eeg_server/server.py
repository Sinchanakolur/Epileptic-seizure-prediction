import asyncio
import websockets
import json
import pandas as pd

# Path to the CHB-MIT preprocessed dataset
DATASET_PATH = '/Users/sahilgadikar/Documents/miniProject/Data/chbmit_preprocessed_data.csv'

try:
    # Load the dataset
    eeg_data = pd.read_csv(DATASET_PATH)
    print("Dataset loaded successfully.")
except Exception as e:
    print(f"Failed to load dataset: {e}")
    eeg_data = pd.DataFrame()  # Use an empty DataFrame as fallback

# EEG Channels
CHANNELS = ["# FP1-F7", "C3-P3", "P3-O1", "P4-O2", "P7-O1", "P7-T7", "T8-P8-0", "T8-P8-1"]

async def eeg_handler(websocket, path):
    print("New client connection established.")
    try:
        for _, row in eeg_data.iterrows():
            # Prepare data to send by extracting only valid EEG channel values
            eeg_values = {channel: row.get(channel, 0.0) for channel in CHANNELS}  # Default to 0 if missing
            eeg_values["timestamp"] = str(pd.Timestamp.now())

            # Send data as JSON
            await websocket.send(json.dumps(eeg_values))
            print("Sent data:", eeg_values)

            await asyncio.sleep(10)  # Send data every 10 seconds

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed by client: {e}")
    except Exception as e:
        print(f"Error during data sending: {e}")
    finally:
        print("Client connection closed.")

async def main():
    try:
        # Start the WebSocket server
        server = await websockets.serve(eeg_handler, "localhost", 8000)
        print("WebSocket server started on ws://localhost:8000")
        await server.wait_closed()
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
