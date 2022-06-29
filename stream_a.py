from regex import P
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn import datasets

import random
import time
import json
from paho.mqtt import client as mqtt_client

broker = 'broker.hivemq.com'
port = 1883
topic = '/superman/monitor'
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'super'
password = '12354678'
mangkok = {}
piring = {}
gelas = {}
gummy = {'pH':[100],'DO':[100],'Salinitas':[100],'Transparansi':[0],'Tinggi_Air':[147],}
slider = pd.DataFrame(gummy)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
            
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
     msg_count = 0
     while True:
         time.sleep(1)
         msg = f"messages: {msg_count}"
         result = client.publish(topic, msg)
         # result: [0, 1]
         status = result[0]
         if status == 0:
             print(f"Send `{msg}` to topic `{topic}`")
         else:
             print(f"Failed to send message to topic {topic}")
         msg_count += 1

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global mangkok
        mangkok = json.loads(msg.payload.decode())
    client.subscribe(topic)
    client.on_message = on_message
    # client.loop_stop()
    
def run_publish():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    
def run_subscribe():
    client = connect_mqtt()
    subscribe(client)
    client.loop_start()

def user_input_features():
    ph = sidehold_ph.slider('pH', 7.6, 9.0, 7.9)
    do = sidehold_do.slider('DO', 4.2, 6.0, 5.36)
    salinitas = sidehold_salinitas.slider('Salinitas', 36.0, 37.0, 36.0)
    transparansi = sidehold_transparansi.slider('Transparansi', 35, 100, 40)
    tinggi_air = sidehold_tinggi.slider('Tinggi Air', 140, 220, 180)
    data = {'pH': ph,
            'DO': do,
            'Salinitas': salinitas,
            'Transparansi': transparansi,
            'Tinggi_Air': tinggi_air}
    features = pd.DataFrame(data, index=[0])

    return features

def slider_monitoring(dataprame):
    sidehold_ph.slider('pH', 7.6, 9.0, float(dataprame['pH']),key=i)
    sidehold_do.slider('DO', 4.2, 6.0, float(dataprame['DO']),key=i)
    sidehold_salinitas.slider('Salinitas', 36.0, 37.0, float(dataprame['Salinitas']),key=i)
    sidehold_transparansi.slider('Transparansi', 35, 100, int(dataprame['Transparansi']),key=i)
    sidehold_tinggi.slider('Tinggi Air', 140, 220, int(dataprame['Tinggi_Air']),key=i)

def last_process(df):
    # home_tabel1.write(df)
    fd = df.copy()
    df['pH']=(df['pH']-5.6)/(9.15-5.6)
    df['DO']=(df['DO']-3.82)/(5.92-3.82)
    df['Salinitas']=(df['Salinitas']-33)/(38-33)
    df['Transparansi']=(df['Transparansi']-30)/(98-30)
    df['Tinggi_Air']=(df['Tinggi_Air']-105)/(220-105)

    # Reads in saved classification model
    prediction = load_clf.predict(df)
    prediction_proba = load_clf.predict_proba(df)

    replacements = {1:'Bagus', 0:'Jelek'}
    replacer = replacements.get  # For faster gets.
    kondisi = [replacer(n, n) for n in prediction]
    
    fd['State'] = pd.DataFrame(kondisi)
    
    home_tabel1.write(fd)

    quality = np.array(['Jelek','Bagus'])
    home_header2.subheader('Prediksi')
    home_tabel2.info(quality[int(prediction[-1])])
    if quality[int(prediction[-1])] == 'Bagus': home_tabel3.info('JAGA KONDISI INI dengan penambahan pupuk setiap minggu')
    else : home_tabel3.info('PERHATIAN!!!....Perlu penggantian air secara berkala dan pemberian kapur dolomit')

    # st.subheader('Probabilitas Prediksi')
    # st.write(prediction_proba)

load_clf = pickle.load(open('streamlit\punyaku\KNN.pkl', 'rb'))

process ='Otomatis Monitoring'

st.write("""
# Support Decision System For Aquaculture Management in Shrimp Cultivation

Sistem ini akan memprediksi kondisi **Kualitas Air**!
""")

process = st.sidebar.selectbox('Pilih Proses Skema',('Manual Input','Otomatis Monitoring'))

side_title = st.sidebar.empty()
sidehold_ph = st.sidebar.empty()
sidehold_do = st.sidebar.empty()
sidehold_salinitas = st.sidebar.empty()
sidehold_transparansi = st.sidebar.empty()
sidehold_tinggi = st.sidebar.empty()

home_header1 = st.empty()
home_tabel1 = st.empty()
home_header2 = st.empty()
home_tabel2 = st.empty()
home_tabel3 = st.empty()

if (process=='Manual Input' ):
    side_title.header('Input **MANUAL** Nilai Parameter Air')
    home_header1.write("""### Tabel Input **MANUAL** Nilai Parameter Air""")
    df = user_input_features()
    last_process(df)

elif(process =='Otomatis Monitoring'):
    i=0
    run_subscribe()
    while i<30 :
        home_header1.write("""### Tabel Input Parameter Air dari **DEVICE**""")
        while gelas == mangkok :
            time.sleep(0.000000001)
        mangkok = [dict([a, [int(x)]] for a, x in b.items()) for b in [mangkok]][0]
        gelas = mangkok.copy()
        if piring == {} : 
            piring = mangkok
        else : 
            for j in mangkok.keys():
                piring['%s'%j].append(mangkok['%s'%j][0])
        df = pd.DataFrame(piring)
        df.iloc[:,0:3] = df.iloc[:,0:3]/100
        slider_monitoring(df.iloc[-1])
        slider = df.iloc[-1]
        last_process(df)
        i=i+1    
        # time.sleep(5)
    
# elif(process =='Otomatis Monitoring'):
#     i=2
#     while i<5 :
#         run_subscribe()
#         print('poin =',i)
#         st.write("""### Tabel Input Parameter Air dari **DEVICE**""")
#         while piring == mangkok || piring.keys:
#             if mangkok == {} : time.sleep(0.000000001)
#             else : 
#                 # df = pd.DataFrame(mangkok)
#                 # df.iloc[:,0:3] = df.iloc[:,0:3]/100
#                 # slider_monitoring(df)
#                 # # asdf = st.sidebar.slider('pH', 7.6, 9.0, float(df['pH'].values))
#                 # # zxcv = st.sidebar.slider('DO', 4.2, 6.0, float(df['DO'].values))
#                 # # qwer = st.sidebar.slider('Salinitas', 36, 37.0, float(df['Salinitas'].values))
#                 # # wert = st.sidebar.slider('Transparansi', 35, 100, int(df['Transparansi'].values))
#                 # # sdfg = st.sidebar.slider('Tinggi Air', 140, 220, int(df['Tinggi_Air'].values))
#                 # last_process(df)
#                 time.sleep(0.000000001)
#         print('iki mangkok',mangkok)
#         mangkok = [dict([a, [int(x)]] for a, x in b.items()) for b in [mangkok]][0]
#         print('iku mangkok',mangkok)
#         print('iki piring',piring)
#         if piring == {} : 
#             piring = mangkok
#         else : 
#             for j in mangkok.keys():
#                 piring['%s'%j].append(mangkok['%s'%j][0])
#         print('iku piring',piring)
#         #piring = [dict([a, [int(x)]] for a, x in b.items()) for b in [piring]][0]
#         df = pd.DataFrame(piring)
#         print(df)
#         df.iloc[:,0:3] = df.iloc[:,0:3]/100
#         slider_monitoring(df.iloc[-1])
#         print('temani-temani')
#         # slider_monitoring(df.iloc[0])
#         # asdf = st.sidebar.slider('pH', 7.6, 9.0, float(df['pH'].values))
#         # zxcv = st.sidebar.slider('DO', 4.2, 6.0, float(df['DO'].values))
#         # qwer = st.sidebar.slider('Salinitas', 36, 37.0, float(df['Salinitas'].values))
#         # wert = st.sidebar.slider('Transparansi', 35, 100, int(df['Transparansi'].values))
#         # sdfg = st.sidebar.slider('Tinggi Air', 140, 220, int(df['Tinggi_Air'].values))
#         last_process(df)
#         print(type(i),i)
#         i=i+1