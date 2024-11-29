import asyncio
import websockets
import json
import pandas as pd
import gdown
import os

# Define the Google Drive file ID (replace with your actual ID)
DRIVE_FILE_ID = '1Lf9Z8xfP3It-jOH4TBwsxanuayKvt79x'  # This is the file ID in quotes

LOCAL_PATH = 'datasets/chbmit_preprocessed_data.csv'
os.makedirs(os.path.dirname(LOCAL_PATH), exist_ok=True)


# Function to download the dataset from Google Drive if it doesn't already exist locally
def download_dataset():
    if not os.path.exists(LOCAL_PATH):
        print("Dataset not found locally, downloading...")
        # Download from Google Drive using the gdown libra1Lf9Z8xfP3Itry
        gdown.download(f'https://drive.google.com/uc?id={DRIVE_FILE_ID}', LOCAL_PATH, quiet=False)

        print("Dataset downloaded successfully.")
    else:
        print("Dataset already exists, skipping download.")

# Call the function to download the dataset
download_dataset()

# Try to load the dataset
try:
    eeg_data = pd.read_csv(LOCAL_PATH)
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
