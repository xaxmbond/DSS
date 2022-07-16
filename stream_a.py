import streamlit as st
import pandas as pd
import numpy as np
import pickle

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
    do = sidehold_do.slider('DO (mg/l)', 4.2, 6.0, 5.36)
    salinitas = sidehold_salinitas.slider('Salinitas (ppm)', 36.0, 37.0, 36.0)
    transparansi = sidehold_transparansi.slider('Transparansi (cm)', 35, 100, 40)
    tinggi_air = sidehold_tinggi.slider('Tinggi Air (cm)', 140, 220, 180)
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
    keterangan_do = ''
    keterangan_ph = ''
    keterangan_sal = ''
    keterangan_trans = ''
    keterangan_penjaga= ''
    rekom_do = ''
    rekom_ph = ''
    rekom_sal = ''
    rekom_trans = ''
    rekom_penjaga= ''
    if quality[int(prediction[-1])] == 'Bagus':
        if float(fd['DO'])<3: 
            keterangan_do = ' Fitoplankton sedang melakukan proses respirasi.'
            rekom_do = ' tambahkan kincir dan pemberian pupuk setiap minggu.'
        if float(fd['pH'])<7.5: 
            keterangan_ph = ' Terdapat ion alumunium di dasar kolam.'
            rekom_ph = ' Taburkan kapur tohor sebanyak 250 sampai 500 kg/ha secara bertahap.'
        if float(fd['Salinitas'])<15:
            keterangan_sal = ' Terlalu banyak ratio air tawar pada permukaan tambak.'
            rekom_sal = ' Lakukan pergantian air.'
        if int(fd['Transparansi'])<25:
            keterangan_trans = ' Populasi plankton menurun.'
            rekom_trans = ' Lakukan penambahan air dari pematang.'
        if keterangan_ph=='' and keterangan_do=='' and keterangan_sal=='' and keterangan_trans=='':
            keterangan_penjaga=' Jumlah fitoplankton sudah cukup.'
            rekom_penjaga=' Tambahkan pupuk setiap minggu.'
        home_tabel3.info('Keadaan tambak bagus dengan kondisi%s%s%s%s%s'%(keterangan_do,keterangan_ph,keterangan_sal,keterangan_trans,keterangan_penjaga))
        home_tabel4.info('JAGA KONDISI INI dan%s%s%s%s%s'%(rekom_do,rekom_ph,rekom_sal,rekom_trans,rekom_penjaga))
    else :
        if float(fd.iloc[-1,:]['DO'])<3: 
            keterangan_do = ' Air kolam mengandung banyak fosfor, amonia, copper dan bahan organik. Banyak zooplankton.'
            rekom_do = ' Tambahkan hidrogen peroksida, pemberian dilakukan secara berulang setiap 2 jam sampai kadar oksigen stabl.'
        if float(fd.iloc[-1,:]['pH'])<7.5: 
            keterangan_ph = ' Terlalu banyak ion alumunium mengendap didasar tanah.'
            rekom_ph = ' Gunakan kapur tohor sebanyak 500 sampai 100 kg/ha.'
        elif float(fd.iloc[-1,:]['pH'])>8.5:
            keterangan_ph = ' Kandungan besi pada tambak meningkat, terdapat fitoplankton beracun (Mycrocystis spp).'
            rekom_ph = ' Gunakan kapur tohor sebanyak 100 sampai 250 kg/ha. Lakukan penggantian air menggunakan air dari pematang secara bertahap.'
        if float(fd.iloc[-1,:]['Salinitas'])<15:
            keterangan_sal = ' Udang kram (bengkok dan berwarna putih).'
            rekom_sal = ' Lakukan pemberian KCL dengan dosis 1 ppm.'
        if int(fd.iloc[-1,:]['Transparansi'])<25:
            keterangan_trans = ' Sedikit populasi plankton dan timbul busa di permukaan air.'
            rekom_trans = ' Lakukan pergantian air dari pematang yang sudah disiapkan atau pengenceran.'
        if keterangan_ph=='' and keterangan_do=='' and keterangan_sal=='' and keterangan_trans=='':
            keterangan_penjaga=' Air terasa lengket.'
            rekom_penjaga=' Perlu penggantian air secara berkala dan pemberian kapur dolomit.'
        home_tabel3.info('Udang tidak nafsu makan,%s%s%s%s%s'%(keterangan_do,keterangan_ph,keterangan_sal,keterangan_trans,keterangan_penjaga))
        home_tabel4.info('PERHATIAN!!!....%s%s%s%s%s'%(rekom_do,rekom_ph,rekom_sal,rekom_trans,rekom_penjaga))

    # st.subheader('Probabilitas Prediksi')
    # st.write(prediction_proba)

load_clf = pickle.load(open('KNN.pkl', 'rb'))

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
home_tabel4 = st.empty()

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
