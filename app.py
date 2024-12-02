import streamlit as st
import pickle
import numpy as np
import websockets
import json
import asyncio
from threading import Thread
import time

# Load the trained model
model = pickle.load(open('EE_model.pkl', 'rb'))

def risk_potability_prediction(input_data):
    """
    Predicts if the patient is affected by an epileptic seizure based on EEG sensor data.
    """
    input_as_array = np.array(input_data).reshape(1, -1)  # Reshape to match model input
    prediction = model.predict(input_as_array)[0]  # Predict the outcome
    return prediction

async def fetch_data_continuous():
    """
    Continuously fetch data from WebSocket, update session state, and make predictions.
    """
    uri = "wss://167f-2401-4900-61bd-4a98-4c2-3a71-2634-8639.ngrok-free.app"
    try:
        async with websockets.connect(uri) as websocket:
            while st.session_state.fetching_data:
                data = await websocket.recv()
                data = json.loads(data)  # Parse the JSON data

                # Update session state EEG data with the latest values
                for key in st.session_state.eeg_data.keys():
                    st.session_state.eeg_data[key] = data.get(key, 0.0)

                # Automatically predict when new data is fetched
                input_data = list(st.session_state.eeg_data.values())
                prediction = risk_potability_prediction(input_data)
                st.session_state.prediction = (
                    'The Patient is affected by an Epileptic Seizure.' if prediction == 0
                    else 'The Patient is not affected by an Epileptic Seizure.'
                )

                # Flag that new data is available
                st.session_state.new_data_available = True

                # Wait for 10 seconds before fetching the next data
                await asyncio.sleep(10)  # Adjust for 10-second interval

    except Exception as e:
        st.error(f"Error occurred while connecting to WebSocket: {e}")

def start_fetching_data():
    """
    Starts the fetch data in a separate thread.
    """
    asyncio.run(fetch_data_continuous())

def main():
    """
    Main function to run the Streamlit app with EEG seizure prediction and WebSocket connection.
    """
    # Streamlit page setup
    st.set_page_config(page_title='EEG - Based Epileptic Seizure Prediction')
    st.title('EEG - Based Epileptic Seizure Prediction')
    st.write('This app predicts whether a patient is experiencing an epileptic seizure based on EEG data.')

    # Initialize session state for EEG data and prediction output if not already set
    if 'eeg_data' not in st.session_state:
        st.session_state.eeg_data = {
            "# FP1-F7": 0.0, "C3-P3": 0.0, "P3-O1": 0.0, "P4-O2": 0.0,
            "P7-O1": 0.0, "P7-T7": 0.0, "T8-P8-0": 0.0, "T8-P8-1": 0.0
        }
    if 'prediction' not in st.session_state:
        st.session_state.prediction = ""
    if 'fetching_data' not in st.session_state:
        st.session_state.fetching_data = False
    if 'new_data_available' not in st.session_state:
        st.session_state.new_data_available = False

    # Start and Stop buttons for fetching data
    if st.button('Start Fetching Data'):
        if not st.session_state.fetching_data:
            st.session_state.fetching_data = True
            # Start fetching data in a background thread
            thread = Thread(target=start_fetching_data)
            thread.start()
        else:
            st.warning("Already fetching data.")

    if st.button('Stop Fetching Data'):
        st.session_state.fetching_data = False

    # Display EEG values as adjustable input fields (for reference)
    st.subheader("Real-Time EEG Data (Adjustable)")
    for key in st.session_state.eeg_data:
        st.session_state.eeg_data[key] = st.number_input(key, value=st.session_state.eeg_data[key], format="%.7f")

    # Show prediction result
    st.subheader('Prediction Result')
    st.write(st.session_state.prediction)

if __name__ == '__main__':
    main()
