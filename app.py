import streamlit as st
import pickle
import numpy as np
import websockets
import json
import asyncio

# Load the trained model
model = pickle.load(open('EE_model.pkl', 'rb'))

# Function for seizure prediction
def risk_potability_prediction(input_data):
    """
    Predicts if the patient is affected by an epileptic seizure based on EEG sensor data.
    """
    input_as_array = np.array(input_data).reshape(1, -1)  # Reshape to match model input
    prediction = model.predict(input_as_array)[0]  # Predict the outcome
    return prediction

# Async function to fetch real-time EEG data
async def fetch_data_continuous():
    """
    Continuously fetch data from WebSocket and update session state.
    """
    uri = "ws://106.51.46.129:8000"  # Ensure this matches the WebSocket server
    try:
        async with websockets.connect(uri) as websocket:
            while st.session_state.fetching_data:
                data = await websocket.recv()
                data = json.loads(data)  # Parse the JSON data
                # Update session state EEG data with the new values
                for key in st.session_state.eeg_data.keys():
                    st.session_state.eeg_data[key] = data.get(key, 0.0)
                st.session_state.new_data_available = True
                await asyncio.sleep(1)  # Prevent high-frequency requests
    except Exception as e:
        st.error(f"Error occurred while connecting to WebSocket: {e}")
    finally:
        st.session_state.fetching_data = False

def start_fetching_data():
    """
    Wrapper function to start the async WebSocket connection.
    """
    asyncio.run(fetch_data_continuous())

# Main function to handle Streamlit UI
def main():
    """
    Streamlit app for seizure prediction and real-time data monitoring.
    """
    # Streamlit page setup
    st.set_page_config(page_title='EEG - Based Epileptic Seizure Prediction')
    st.title('EEG - Based Epileptic Seizure Prediction')
    st.write('This app predicts whether a patient is experiencing an epileptic seizure based on EEG data.')

    # Initialize session state for EEG data and prediction output
    if 'eeg_data' not in st.session_state:
        st.session_state.eeg_data = {
            "FP1-F7": 0.0, "C3-P3": 0.0, "P3-O1": 0.0, "P4-O2": 0.0,
            "P7-O1": 0.0, "P7-T7": 0.0, "T8-P8-0": 0.0, "T8-P8-1": 0.0
        }
    if 'prediction' not in st.session_state:
        st.session_state.prediction = ""
    if 'fetching_data' not in st.session_state:
        st.session_state.fetching_data = False
    if 'new_data_available' not in st.session_state:
        st.session_state.new_data_available = False

    # Toggle between manual and real-time mode
    mode = st.radio("Select Mode", options=["Manual Entry", "Real-Time Data"])

    # Manual entry fields
    if mode == "Manual Entry":
        st.subheader("Enter EEG Values Manually")
        for key in st.session_state.eeg_data:
            st.session_state.eeg_data[key] = st.number_input(key, value=st.session_state.eeg_data[key], format="%.7f")

    # Real-time EEG data monitoring
    elif mode == "Real-Time Data":
        st.write("Fetching real-time data from WebSocket...")
        if st.button('Start Fetching Data'):
            st.session_state.fetching_data = True
            start_fetching_data()
        if st.button('Stop Fetching Data'):
            st.session_state.fetching_data = False

    # Predict button to run prediction on the fetched or manually entered data
    if st.button('Predict'):
        input_data = list(st.session_state.eeg_data.values())
        prediction = risk_potability_prediction(input_data)
        st.session_state.prediction = (
            'The Patient is affected by an Epileptic Seizure.' if prediction == 1
            else 'The Patient is not affected by an Epileptic Seizure.'
        )
        st.session_state.new_data_available = False

    # Show prediction result
    st.subheader('Prediction Result')
    st.write(st.session_state.prediction)

# Corrected entry point
if __name__ == '__main__':
    main()


