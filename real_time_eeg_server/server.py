import asyncio
import websockets
import numpy as np
import json

# Fields as per your frontend interface
CHANNELS = ["FP1-F7", "C3-P3", "P3-O1", "P4-O2", "P7-O1", "P7-T7", "T8-P8-O"]

# WebSocket handler to send simulated EEG data
async def eeg_handler(websocket, path):
    print("New connection established.")
    try:
        while True:
            # Simulate data for each channel
            simulated_data = {channel: np.random.random() * 100 for channel in CHANNELS}
            simulated_data["timestamp"] = str(np.datetime64('now'))  # Adding timestamp
            
            # Send the simulated data
            await websocket.send(json.dumps(simulated_data))
            print("Sent data:", simulated_data)
            
            await asyncio.sleep(1)  # Send data every 1 second
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        print("Connection closed.")

# Main server function
async def main():
    server = await websockets.serve(eeg_handler, "localhost", 8080)
    print("WebSocket server started on ws://localhost:8080")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
