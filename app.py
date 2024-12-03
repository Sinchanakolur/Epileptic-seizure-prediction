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

async def fetch_and_predict(uri):
    """
    Fetch data from the WebSocket continuously and make predictions in real-time.
    """
    try:
        async with websockets.connect(uri) as websocket:
            while True:  # Keep the connection open
                data = await websocket.recv()  # Receive data from WebSocket
                data = json.loads(data)  # Parse the JSON data

                # Update EEG data in session state
                for key in st.session_state.eeg_data.keys():
                    st.session_state.eeg_data[key] = data.get(key, 0.0)

                # Predict with new data
                input_data = list(st.session_state.eeg_data.values())
                prediction = risk_potability_prediction(input_data)
                result = (
                    f"**<span style='color:#FF4D4D;'>The Patient is affected by an Epileptic Seizure.</span>**"
                    if prediction == 0
                    else "**The Patient is not affected by an Epileptic Seizure.**"
                )

                # Append the prediction result to session state
                st.session_state.prediction_results.append(result)

                # Render the updated results
                st.experimental_rerun()

                await asyncio.sleep(10)  # Wait for the next batch of data (every 10 seconds)

    except Exception as e:
        st.error(f"WebSocket connection error: {e}")

def main():
    """
    Main function to run the Streamlit app with real-time EEG seizure prediction.
    """
    # Streamlit page setup
    st.set_page_config(
        page_title='EEG Seizure Prediction',
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title('🧠 EEG-Based Epileptic Seizure Prediction')
    st.markdown(
        """
        <p style="font-size:18px;">
        This app predicts whether a patient is experiencing an epileptic seizure based on EEG data. 
        It fetches real-time EEG data, processes it, and provides a prediction.
        </p>
        """, unsafe_allow_html=True
    )

    # Sidebar for Navigation
    st.sidebar.header("Navigation")
    st.sidebar.markdown(
        """
        <ul style="list-style-type:circle; font-size:15px;">
            <li><a href="#real-time-eeg-data" style="text-decoration:none;">Real-Time EEG Data</a></li>
            <li><a href="#prediction-results" style="text-decoration:none;">Prediction Results</a></li>
        </ul>
        """, unsafe_allow_html=True
    )

    # Initialize session state variables
    if 'eeg_data' not in st.session_state:
        st.session_state.eeg_data = {
            "# FP1-F7": 0.0, "C3-P3": 0.0, "P3-O1": 0.0, "P4-O2": 0.0,
            "P7-O1": 0.0, "P7-T7": 0.0, "T8-P8-0": 0.0, "T8-P8-1": 0.0
        }
    if 'prediction_results' not in st.session_state:
        st.session_state.prediction_results = []
    if 'fetching_data' not in st.session_state:
        st.session_state.fetching_data = False

    # Layout for EEG data
    st.subheader("Real-Time EEG Data (Adjustable)")
    st.markdown(
        """
        <p style="font-size:15px;">
        You can adjust the EEG values manually for testing or allow real-time data fetching to update them automatically.
        </p>
        """, unsafe_allow_html=True
    )
    cols = st.columns(4)  # Layout the input fields into columns
    for i, key in enumerate(st.session_state.eeg_data):
        with cols[i % 4]:
            st.session_state.eeg_data[key] = st.number_input(
                label=key, 
                value=st.session_state.eeg_data[key], 
                format="%.7f",
                help=f"Current value for {key}"
            )

    # Start/Stop Data Fetching
    uri = "wss://167f-2401-4900-61bd-4a98-4c2-3a71-2634-8639.ngrok-free.app"

    st.markdown("---")
    if st.session_state.fetching_data:
        st.button("Stop Fetching Data", on_click=lambda: setattr(st.session_state, 'fetching_data', False))
        st.info("Fetching and predicting in real-time...")
    else:
        if st.button("Start Fetching and Predicting"):
            st.session_state.fetching_data = True
            asyncio.run(fetch_and_predict(uri))

    # Display Prediction Results
    st.subheader("Prediction Results")
    st.markdown(
        """
        <p style="font-size:15px;">
        Below are the predictions based on the received EEG data. 
        The results are updated in real-time as new data is fetched.
        </p>
        """, unsafe_allow_html=True
    )
    if st.session_state.prediction_results:
        for result in reversed(st.session_state.prediction_results):
            st.markdown(f"{result}", unsafe_allow_html=True)
    else:
        st.info("No predictions yet. Start fetching data to see results.")

if __name__ == '__main__':
    main()



