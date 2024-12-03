import streamlit as st
import pickle
import numpy as np
import websockets
import json
import asyncio

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
    Continuously fetch data from WebSocket and update session state.
    """
    uri = "wss://167f-2401-4900-61bd-4a98-4c2-3a71-2634-8639.ngrok-free.app"
    try:
        async with websockets.connect(uri) as websocket:
            while st.session_state.fetching_data:
                data = await websocket.recv()  # Receive data from WebSocket
                data = json.loads(data)  # Parse the JSON data

                # Update session state EEG data if new data is fetched
                for key in st.session_state.eeg_data.keys():
                    st.session_state.eeg_data[key] = data.get(key, 0.0)

                # Predict with new data
                input_data = list(st.session_state.eeg_data.values())
                prediction = risk_potability_prediction(input_data)
                result = (
                    f"Prediction: The Patient is affected by an Epileptic Seizure."
                    if prediction == 0
                    else "Prediction: The Patient is not affected by an Epileptic Seizure."
                )

                # Add prediction to results list
                st.session_state.prediction_results.append(result)

                await asyncio.sleep(10)  # Wait for the next batch of data (every 10 seconds)
    except Exception as e:
        st.error(f"Error occurred while connecting to WebSocket: {e}")

def main():
    """
    Main function to run the Streamlit app with EEG seizure prediction and WebSocket connection.
    """
    # Streamlit page setup
    st.set_page_config(page_title='EEG Seizure Prediction', layout="wide")
    st.title('🧠 EEG-Based Epileptic Seizure Prediction')
    st.write("This app predicts whether a patient is experiencing an epileptic seizure based on EEG data.")

    # Initialize session state for EEG data and prediction results if not already set
    if 'eeg_data' not in st.session_state:
        st.session_state.eeg_data = {
            "# FP1-F7": 0.0, "C3-P3": 0.0, "P3-O1": 0.0, "P4-O2": 0.0,
            "P7-O1": 0.0, "P7-T7": 0.0, "T8-P8-0": 0.0, "T8-P8-1": 0.0
        }
    if 'prediction_results' not in st.session_state:
        st.session_state.prediction_results = []
    if 'fetching_data' not in st.session_state:
        st.session_state.fetching_data = False

    # Layout for data and actions
    col1, col2 = st.columns([2, 1])

    # Column 1: EEG Data and Controls
    with col1:
        st.subheader("Real-Time EEG Data")
        st.write("Adjust EEG values manually or wait for live data.")
        for key in st.session_state.eeg_data:
            st.session_state.eeg_data[key] = st.number_input(
                label=key, 
                value=st.session_state.eeg_data[key], 
                format="%.7f"
            )

        # Buttons to start and stop fetching data
        if st.button('▶️ Start Fetching Data', key="start_fetch"):
            st.session_state.fetching_data = True
            asyncio.run(fetch_data_continuous())

        if st.button('⏹️ Stop Fetching Data', key="stop_fetch"):
            st.session_state.fetching_data = False

    # Column 2: Prediction Results
    with col2:
        st.subheader("Predictions")
        if st.session_state.prediction_results:
            st.write("Results of the predictions will appear here:")
            for result in reversed(st.session_state.prediction_results):
                st.info(result)
        else:
            st.write("No predictions yet. Start fetching data or adjust EEG values manually.")

if __name__ == '__main__':
    main()


