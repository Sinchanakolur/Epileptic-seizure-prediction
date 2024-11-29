import asyncio
import websockets
import json
import pandas as pd

# Path to the CHB-MIT preprocessed dataset
DATASET_PATH = r'D:\simpledev\chbmit_preprocessed_data.csv'

# EEG Channels (ensure these match your dataset columns)
CHANNELS = ["# FP1-F7", "C3-P3", "P3-O1", "P4-O2", "P7-O1", "P7-T7", "T8-P8-0", "T8-P8-1"]

def load_dataset(path):
    """
    Load the EEG dataset and ensure it contains required channels.
    """
    try:
        data = pd.read_csv(path)
        missing_channels = [channel for channel in CHANNELS if channel not in data.columns]
        if missing_channels:
            raise ValueError(f"Dataset is missing required channels: {missing_channels}")
        print("Dataset loaded successfully.")
        return data
    except Exception as e:
        print(f"Failed to load dataset: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure

# Load the dataset
eeg_data = load_dataset(DATASET_PATH)

async def eeg_handler(websocket, path):
    """
    WebSocket handler to stream EEG data row by row.
    """
    print("New client connection established.")
    try:
        for _, row in eeg_data.iterrows():
            # Prepare data to send by extracting valid EEG channel values
            eeg_values = {channel: row[channel] for channel in CHANNELS}
            eeg_values["timestamp"] = pd.Timestamp.now().isoformat()  # Add a timestamp

            # Send data as JSON
            await websocket.send(json.dumps(eeg_values))
            print("Sent data:", eeg_values)

            await asyncio.sleep(1)  # Send data every 1 second (adjust as needed)

    except websockets.exceptions.ConnectionClosedError:
        print("Connection closed by client.")
    except Exception as e:
        print(f"Error during data sending: {e}")
    finally:
        print("Client connection closed.")

async def main():
    """
    Main function to start the WebSocket server.
    """
    try:
        server = await websockets.serve(eeg_handler, "localhost", 8000)
        print("WebSocket server started on ws://localhost:8000")
        await server.wait_closed()
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
