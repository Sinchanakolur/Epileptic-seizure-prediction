import streamlit as st
import pickle
import numpy as np
import asyncio
import websockets
import json

# Load the trained model
model = pickle.load(open('EE_model.pkl', 'rb'))

def risk_potability_prediction(input_data):
    """
    This function takes in EEG sensor data and predicts whether the patient is affected by an epileptic seizure.
    """
    input_as_array = np.array(input_data).reshape(1, -1)  # Reshape to match model input
    prediction = model.predict(input_as_array)[0]  # Predict the outcome
    return prediction

async def fetch_data():
    """
    This asynchronous function connects to the WebSocket server and receives real-time EEG data.
    """
    uri = "ws://localhost:8080"  # WebSocket server URL
    try:
        # Connect to the WebSocket server
        async with websockets.connect(uri) as websocket:
            while True:
                data = await websocket.recv()  # Receive data from WebSocket
                data = json.loads(data)  # Parse the JSON data
                st.write(f"EEG Value: {data['eegValue']} at {data['timestamp']}")  # Display the received data
                await asyncio.sleep(1)  # Sleep for 1 second before receiving the next data
    except Exception as e:
        st.error(f"Error occurred: {e}")

def main():
    """
    Main function to run the Streamlit app with EEG seizure prediction and WebSocket connection.
    """
    # Streamlit page setup
    st.set_page_config(page_title='EEG - Based Epileptic Seizure Prediction')
    st.title('EEG - Based Epileptic Seizure Prediction')
    st.write('This app predicts whether a patient is experiencing an epileptic seizure based on EEG data.')
    
    # Input fields for EEG sensor data
    st.subheader('Epileptic Seizure Prediction')
    mar = st.number_input('# FP1-F7', format="%.7f", min_value=0.0, max_value=100.0, value=7.0, step=0.1)
    deb = st.number_input('C3-P3', format="%.7f", min_value=0.0, value=50.0, step=1.0)
    dis = st.number_input('P3-O1', format="%.7f", min_value=0.0, value=50.0, step=1.0)
    gen = st.number_input('P4-O2', format="%.7f", min_value=-0.0000303, value=50.0, step=1.0)
    crs = st.number_input('P7-O1', format="%.7f", min_value=0.0, max_value=1000.0, step=1.0)
    gdp = st.number_input('P7-T7', format="%.7f", min_value=-0.0000303, value=50.0, step=1.0)
    pqg = st.number_input('T8-P8-0', format="%.7f", min_value=0.0, value=50.0, step=1.0)
    pqg1 = st.number_input('T8-P8-1', format="%.7f", min_value=0.0, value=50.0, step=1.0)
   
    # Prediction button
    if st.button('Predict'):
        input_data = [mar, deb, dis, gen, crs, gdp, pqg, pqg1]
        prediction = risk_potability_prediction(input_data)
        if prediction == 0:
            st.error('The Patient is affected by Epileptic Seizure.')
        else:
            st.success('The Patient is not affected by Epileptic Seizure.')

    # WebSocket connection to receive real-time EEG data
    st.write("Connecting to WebSocket for real-time EEG data...")
    asyncio.run(fetch_data())  # Run the WebSocket function to fetch data asynchronously

if __name__ == '__main__':
    main()
