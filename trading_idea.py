# coding=utf-8
from pickle import FALSE
from random import seed
from random import random
import math as m
from time import process_time
from scipy.stats import norm
from random import randrange
import quantumrandom 
import numpy as np
from bitarray import bitarray
from bitarray.util import int2ba
import streamlit as st
import pandas as pd
import altair as alt
import base64
import xlsxwriter
from io import BytesIO
#import plotly.figure_factory as ff



output = BytesIO()


st.set_page_config(page_title="My Webpage", page_icon=":tada:", layout="wide")
#st.write("""
    # Meine App
    #Hello *world!*
    #""")
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.write("""# Vergleich von Buy and Hold vs. Trading""")
#st.markdown("***")
st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

#ergebnis_placeholder = st.empty()

def binary(num, pre='0b', length=12, spacer=0):   #12
    return '{{:{0}>{1}}}'.format(spacer, length).format(bin(num)[2:])


def lognorm(x,mu,sigma):
    a = (m.log(x) - mu)/m.sqrt(2*sigma**2)
    p = 0.5 + 0.5*m.erf(a)
    return p





def main():
    output = "empty"
    up = 0.0
    down = 0.0
  
    #verlaufArray = [4096][12]

    counter_trading_diskret = 0
    counter_buyAndHold_diskret = 0
    counter_indifferent_diskret = 0
    summe_trading_diskret = 0
    summe_buyAndHold_diskret = 0
    summe_indifferent_diskret = 0
    spalte1, spalte2 = st.columns(2)
    kredit_faktor = 0
    kredit_kondition = 0
    kredit_BH = False
    kredit_rueckzahlung = "zum Laufzeitende"
    kredit_ausloeser = 0.3
    anzahl_simulationen = 100
    #handelstage = 52

    diskret = '<p style="font-family:sans-serif; color:black; font-size: 30px;"><i>Simulation - klassisch mit Wahrscheinlichkeiten</i></p>'
    st.markdown(diskret, unsafe_allow_html=True)
    st.write("[Mehr zur Generierung echter Zufallszahlen (Quantenvakuum-Fluktuation) >](https://qrng.anu.edu.au/)")

    #st.text_input('Sigma: ')
    #st.text_input('Mu: ')
    #st.selectbox('Zufallszahlen: ', ["Echte ANU","Pseudo","Pseudo-System"])

    # Stetig nicht abzählbar - Trading vs Buy and Hold 
    
    with st.expander("Simulationseinstellungen"):
        left, right = st.columns(2)
        with left:
            #st.text_input('Sigma: ')
            zeitraum = st.number_input('Simulierter Zeitraum T (in Jahren): ', 0, 10, value=5) 
            anzahl_simulationen = st.number_input('Anzahl an Simulationsläufen (max. 1000): ', 1, 1000, value=100)
            sigma = st.number_input('Volatilität/Sigma σ: ', 0.0, 1.0, value=0.2)
            art_der_zufallszahlen = st.selectbox('Art der Zufallszahlen: ', ["Pseudo Zufallszahlen","Immer-Gleiche Pseudo Zufallszahlenfolge (gleicher Seed)","Echte Zufallszahlen (Quantenfluktuation)"])
        with right:
            #st.text_input('Mu: ')
            handelstage = st.number_input('Handelstage pro Jahr (z.B. 52 = Wochenweise, 260 = Tageweise...): ', 0, 260, value=52) 
            price = st.number_input('Aktienkurs in € (zu Beginn)', 0, 1000, value= 100)
            my = st.number_input('Drift/Mu µ: ', 0.0, 1.0, value= 0.08)
           
            
    #ergebnis_placeholder = st.empty()
    with st.expander("Handelsstrategie wählen"):
        ausgewaehlte_strategie = st.selectbox('Handelsstrategie: ', ["Siganlgrenzen für Wahrscheinlichkeiten","38/200 Tagelinie (noch nicht implementiert)","MACD (noch nicht implementiert)"])
        left_2, right_2 = st.columns(2)
        with left_2:
            if "Siganlgrenzen für Wahrscheinlichkeiten" in ausgewaehlte_strategie:
                signalgrenze_verkauf = st.number_input('Signalgrenze "VERKAUFEN" (in %, verkaufen wenn überhalb dieser Grenze): ', 0.0, 1.0, value= 0.60)

        with right_2:
            if "Siganlgrenzen für Wahrscheinlichkeiten" in ausgewaehlte_strategie:
                signalgrenze_kauf = st.number_input('Signalgrenze "KAUFEN" (in %, kaufen wenn unterhalb dieser Grenze): ', 0.0, 1.0, value= 0.30)
         


    with st.expander("Leverage mit Kredit (Optional)"):
        #kredit_true = st.checkbox("Kreditaufnahme (ja/nein)", value=False)
        left_3, right_3 = st.columns(2) 
        with left_3:
            kredit_true = st.checkbox("Kreditaufnahme (ja/nein)", value=False)
            if kredit_true:
                kredit_faktor = st.number_input('Kreditaufnahme (x-fache des Start-Aktienkurses): ', 0.0, 20.0, value=0.5)
                kredit_ausloeser = st.number_input('Kreditausloese-Ereignis (Signalgrenze "Kaufen"): ', 0.0, 1.0, value= 0.30)
        with right_3:
            if kredit_true:
                kredit_reinvest = st.checkbox("Gewinn (durch Kredit) reinvestieren (ja/nein)", value=False)
                #kredit_BH = st.checkbox("Kreditaufnahme auch für Buy and Hold Strategie (ja/nein)", value=False)
                kredit_kondition =  st.number_input('Kreditkondition (in Prozent p.a.): ', -0.5, 1.0, value=0.01) / handelstage
                kredit_rueckzahlung = st.selectbox('Kreditrueckzahlung (Zeitpunkt): ',('zum Laufzeitende', 'bei Verkauf-Signalgrenze (mehrfache Kreditaufnahme möglich)'))
                

    kredit = kredit_faktor * price


    if st.button('Simulation durchführen'):
        my_bar = st.progress(0)
        with st.spinner('Bitte warten...'):
            #@st.cache(show_spinner=True)
            #my = 0.08
            #sigma = 0.2
            #St = 120
            #min = a if a < b else b
            t = float(1.0/handelstage)
            up = signalgrenze_verkauf if "Siganlgrenzen für Wahrscheinlichkeiten" in ausgewaehlte_strategie else 0.6  #Signalgrenze (in abhängigkeit der Wahrscheinlichkeit) für den Verkauf --> Verkaufsignal z.B. wenn >= 60%
            down = signalgrenze_kauf if "Siganlgrenzen für Wahrscheinlichkeiten" in ausgewaehlte_strategie else 0.3 #Signalgrenze (in abhängigkeit der Wahrscheinlichkeit) für den Kauf --> Kaufsignal z.B. wenn <= 30%

            countBH = 0
            countTS = 0
            #countTS_mit_leverage = 0
            #countBH_mit_leverage = 0
            countTS_kredit_aktiv = 0
            countTS_Kredit_gewinn = 0
            betragBH = 0
            betragTS = 0
            betragTS_mit_Leverage = 0
            betrag_kredit_gewinn_all = 0
            betragTS_kredit = 0
            zf = randrange(100)
            print(zf)
            #endwerte_sim = [0] * 260
            endwerte_sim = np.zeros(shape=(int(anzahl_simulationen),3)) # 4096,12
            endwerte_sim_ohne = np.zeros(shape=(int(anzahl_simulationen),2)) # 4096,12
            endwerte_sim_trading = [0] * int(anzahl_simulationen) # 4096,12
            endwerte_sim_buyandhold = [0] * int(anzahl_simulationen) # 4096,12
            #print(norm.ppf(0.95)) entspricht StandNormInv in Excel
            handelstage_gesamt = int(handelstage * zeitraum)

            ergebnis_array = np.zeros(shape=(int(10),5))  # 0 Häufigkeit (BH,TS,%BH,%TS,performanceTS), 1 Betrag/Summe (BH,TS,%BH,%TS,performanceTS), 2
            ergebnis_array_kredit = np.zeros(shape=(int(10),5)) # 0 Häufigkeit, 1 Betrag/Summe (BH,TS,%TS), 2 Summe der Gewinne nur durch Kredit
            ergebnis_array_transaktionsgebühr = np.zeros(shape=(int(10),5))
            #np.array([[countBH, countTS],[countBH_mit_leverage, countTS_mit_leverage], [betragBH_rund, betragTS_rund],[betragBH_rund,betragTS_mit_Leverage], [0,betrag_kredit_gewinn_all_rund]])




### Falls gleiche Zufallszahlenfolge gewünscht wird ### 
            if "Default-Zufallszahlenfolge mit gleichem Seed" in art_der_zufallszahlen:
                zufallszahlen_Set = np.zeros(shape=(int(anzahl_simulationen),handelstage_gesamt)) # 4096,12
                sed = seed(4)
                for u in range(anzahl_simulationen):
                    for p in range(handelstage_gesamt):
                        zufallszahlen_Set[u][p] = random()


            for i in range(int(anzahl_simulationen)):
                my_bar.progress((i+1)/anzahl_simulationen)
                seed(i+zf+10)
                #handelstage_gesamt = handelstage * zeitraum
                randomNum = [0] * handelstage_gesamt      # Aray der Zufallszahlen [0;1]
                process = [0.0] * handelstage_gesamt      # Array für die Aktienkurse / Prozess
                position = [0.0] * handelstage_gesamt
                cash = [0.0] * handelstage_gesamt
                prob = [0.0] * handelstage_gesamt
                signal = [0.0] * handelstage_gesamt
                possible = [0.0] * handelstage_gesamt
                golden = [0.0] * handelstage_gesamt 
                kreditlinie = [0.0] * handelstage_gesamt 
                kredit_cash = [0.0] * handelstage_gesamt 
                kredit_position = [0.0] * handelstage_gesamt 
                kredit_kurs = [0.0] * handelstage_gesamt
                kredit_gewinn = [0.0] * handelstage_gesamt
                # 500 Zufallszahlen werden erzeugt
                randomNum[0] = int(1)

                process[0] = price
                position[0] = 0
                cash[0] = price #100.0
                golden[0] = price #100.0
                kredit_aktiv = False
                kredit_gewinn_all = 0
                kredit_gewinn_zw = 0
                kredit_ende = False

            #"""  
       
                if "Echte Zufallszahlen (Quantenfluktuation)" in art_der_zufallszahlen: 
                    if handelstage_gesamt < 1000:
                        myList = quantumrandom.get_data(data_type='uint16', array_length=handelstage_gesamt)
                    else:
                        myList = quantumrandom.get_data(data_type='uint16', array_length=1000)
                        if handelstage_gesamt > 1000: 
                            myList2 = quantumrandom.get_data(data_type='uint16', array_length=1000)
                            myList += myList2
                        if handelstage_gesamt > 2000: 
                            myList3 = quantumrandom.get_data(data_type='uint16', array_length=1000)
                            myList += myList3
                        if handelstage_gesamt > 3000: 
                            myList4 = quantumrandom.get_data(data_type='uint16', array_length=1000)
                            myList += myList4
                    myInt = 65535.0
                    newList  = np.divide(myList, myInt)
                        
                for rand in range(len(randomNum)):

                    if "Pseudo Zufallszahlen" in art_der_zufallszahlen: randomNum[rand] = random() # Mit Random from Python
                    elif "Echte Zufallszahlen (Quantenfluktuation)" in art_der_zufallszahlen: 
                        randomNum[rand] = newList[rand] # Mit Quantenfluktuationszahlen
                        #print(randomNum[rand])
                    elif "Immer-Gleiche Pseudo Zufallszahlenfolge (gleicher Seed)" in art_der_zufallszahlen:
                        randomNum[rand] = zufallszahlen_Set[i][rand]
                    else: randomNum[rand] = random()


                    #runningTime[rand] = float((rand+1) * t)
                    if rand > 0: 
                        process[rand] = process[rand-1] * m.exp((my - (sigma**2)/2) * t + sigma * m.sqrt(t) * norm.ppf(randomNum[rand]))
                        #print(process[rand])
                        #prob[rand] = norm.sf(process[rand], m.log(price)+(my+(sigma**2)/2)*rand*t, sigma * m.sqrt(rand*t))
                        prob[rand] = lognorm(process[rand], m.log(price)+(my+(sigma**2)/2)*rand*t, sigma * m.sqrt(rand*t))
                        #print(prob[rand])
                        # Einschätzung ob Kauf oder Verkaufssignal vorhanden
                        if prob[rand] < down:
                            signal[rand] = "Kauf"
                        elif prob[rand] > up:
                            signal[rand] = "Verkauf" 
                        else:
                            signal[rand] = "-" 

                        # Kauf oder Verkauf überhaupt möglich (Cash zum einsteigen oder schon investiert)?
                        if signal[rand] == "Kauf" and cash[rand-1] > 0:
                            possible[rand] = "möglich"
                        elif signal[rand] == "Kauf" and cash[rand-1] <= 0:
                            possible[rand] = "nicht möglich" 
                        elif signal[rand] == "Verkauf" and position[rand-1] > 0:
                            possible[rand] = "möglich"
                        elif signal[rand] == "Verkauf" and position[rand-1] <= 0:     # funktioniert evtl. nicht wenn der Aktien-Kurs/Prozess ins minus geht --> eher unwahrscheinlich
                            possible[rand] = "nicht möglich"
                        else:
                            possible[rand] = "-" 




# Falls kein Kredit

                        if not kredit_true: 
                            # Position aufbauen/abbauen, je nach Signal von oben (Signal + möglich)
                            if signal[rand] == "Kauf" and possible[rand] == "möglich":
                                position[rand] = cash[rand-1]/process[rand]   

                            elif signal[rand] == "Verkauf" and possible[rand] == "möglich":
                                position[rand] = 0
                            else: 
                                position[rand] = position[rand-1]

                            # Cash
                            if signal[rand] == "Verkauf" and possible[rand] == "möglich":
                                cash[rand] = process[rand] * position[rand-1]
                                
                            elif signal[rand] == "Kauf" and possible[rand] == "möglich":
                                cash[rand] = 0
                            else: 
                                cash[rand] = cash[rand-1]
                        else:
# Falls mit Kredit
# 1. Möglichkeit
                            if 'bei Verkauf-Signalgrenze (mehrfache Kreditaufnahme möglich)' in kredit_rueckzahlung :
                                #Kreditaufnahme
                                if prob[rand] < kredit_ausloeser and not kredit_aktiv:
                                    kreditlinie[rand] = kredit
                                    kredit_position[rand] = kreditlinie[rand]/process[rand]
                                    kredit_aktiv = True
                                elif kredit_aktiv:
                                    kreditlinie[rand] = kreditlinie[rand-1] + kredit * kredit_kondition # Zinsen werden addiert
                                    #print(kredit * kredit_kondition)
                                    kredit_kurs[rand] = kredit_position[rand] * process[rand]
                                    kredit_position[rand] = kredit_position[rand-1]
                                else:
                                    kreditlinie[rand] = 0.0


                                # Position aufbauen/abbauen, je nach Signal von oben (Signal + möglich)
                                if signal[rand] == "Kauf" and possible[rand] == "möglich":
                                    position[rand] = cash[rand-1]/process[rand]   

                                elif signal[rand] == "Verkauf" and possible[rand] == "möglich":
                                    position[rand] = 0
                                else: 
                                    position[rand] = position[rand-1]

                                # Cash
                                if (signal[rand] == "Verkauf" and possible[rand] == "möglich") or (rand == handelstage_gesamt-1 and kredit_aktiv):
                                    cash[rand] = process[rand] * position[rand-1]
                                    if kredit_aktiv:
                                        kredit_cash[rand] = process[rand] * kredit_position[rand-1]
                                        kredit_aktiv = False
                                        kredit_gewinn[rand] =  kredit_cash[rand] - kreditlinie[rand] 
                                        kredit_gewinn_all += kredit_gewinn[rand]
                                elif signal[rand] == "Kauf" and possible[rand] == "möglich":
                                    cash[rand] = 0
                                else: 
                                    cash[rand] = cash[rand-1]
                                    kredit_cash[rand] = kredit_cash[rand-1]
                            


    # 2. Möglichkeit
                            if 'zum Laufzeitende' in kredit_rueckzahlung:
                                #Kreditaufnahme
                                if prob[rand] < kredit_ausloeser and not kredit_aktiv and not kredit_ende:
                                    kreditlinie[rand] = kredit
                                    kredit_position[rand] = kreditlinie[rand]/process[rand]
                                    kredit_aktiv = True
                                elif kredit_aktiv:
                                    kreditlinie[rand] = kreditlinie[rand-1] + kredit * kredit_kondition # Zinsen werden addiert
                                    kredit_kurs[rand] = kredit_position[rand] * process[rand]
                                    if kredit_ende:
                                        kredit_position[rand] = 0
                                    else:
                                        kredit_position[rand] = kredit_position[rand-1]
                                else:
                                    kreditlinie[rand] = 0.0

                                # Position aufbauen/abbauen, je nach Signal von oben (Signal + möglich)
                                if signal[rand] == "Kauf" and possible[rand] == "möglich":
                                    position[rand] = cash[rand-1]/process[rand]   

                                elif signal[rand] == "Verkauf" and possible[rand] == "möglich":
                                    position[rand] = 0
                                else: 
                                    position[rand] = position[rand-1]

                                # Cash
                                if signal[rand] == "Verkauf" and possible[rand] == "möglich":
                                    cash[rand] = process[rand] * position[rand-1]
                                    if kredit_aktiv and not kredit_ende:
                                        kredit_cash[rand] = process[rand] * kredit_position[rand-1]
                                        #print("Kredit_CASHHHH:" + str(kredit_cash[rand]))
                                        kredit_aktiv = True
                                        kredit_gewinn_zw = kredit_cash[rand]
                                        kredit_ende = True
                                        #kredit_gewinn_all += kredit_gewinn[rand]
                                elif signal[rand] == "Kauf" and possible[rand] == "möglich":
                                    cash[rand] = 0
                                else: 
                                    cash[rand] = cash[rand-1]
                                    kredit_cash[rand] = kredit_cash[rand-1]





                        # Golden
                        if position[rand] > 0:
                            golden[rand] = position[rand] * process[rand]
                        else:
                            golden[rand] = cash[rand] 
                        #print(str(signal[rand]) + " | " + str(prob[rand]) + " | " + str(possible[rand]) + " | " + str(golden[rand]))
                        #print(str(process[rand]) + " | " + str(golden[rand]))
                         
                # falls am Ende noch nicht verkauft wurde, wird es hier gemacht und der Kredit zurückgezahlt inkl. Zinsen         
                if kredit_true:  
                    if rand == (handelstage_gesamt-1) and kredit_aktiv and not kredit_ende:
                                            kredit_cash[rand] = process[rand] * kredit_position[rand-1]
                                            #print("Kredit_CASHHHH:" + str(kredit_cash[rand]))
                                            kredit_aktiv = True
                                            kredit_gewinn_zw = kredit_cash[rand]
                                            kredit_ende = True

                    if 'zum Laufzeitende' in kredit_rueckzahlung:
                        kredit_gewinn_all = kredit_gewinn_zw - kreditlinie[handelstage_gesamt-1]


                    #Mit Leverage
                    endwerte_sim[i][2] = kredit_gewinn_all # Trading nur mit Kredit
                    #betragTS_mit_Leverage += round(golden[handelstage_gesamt-1]+kredit_gewinn_all,2)
                    ergebnis_array_kredit[1][1] += round(golden[handelstage_gesamt-1]+kredit_gewinn_all,2)
                    betrag_kredit_gewinn_all += round(kredit_gewinn_all,2)
                    if (golden[handelstage_gesamt-1]+kredit_gewinn_all) > process[handelstage_gesamt-1]:
                        #countTS_mit_leverage = countTS_mit_leverage +1
                        ergebnis_array_kredit[0][1] += 1
                    else:
                        #countBH_mit_leverage = countBH_mit_leverage +1
                        ergebnis_array_kredit[0][0] += 1

                    if not kredit_gewinn_all == 0:
                        countTS_kredit_aktiv += 1
                    if kredit_gewinn_all > 0:
                        countTS_Kredit_gewinn += 1
                    

                # Excel beispiel Rechnung zum nachvollziehen
                if kredit_true: 
                    daten_klassisch = np.array([np.transpose(process),np.transpose(signal), np.transpose(possible), np.transpose(position),np.transpose(cash), np.transpose(golden), np.transpose(kreditlinie), np.transpose(kredit_position), np.transpose(kredit_gewinn)])
                    column = ('Prozess (bzw. Buy and Hold)', 'Signal', 'Kauf-Möglich?', 'Position', 'Cash-Bestand','Trading-Position', 'kreditlinie', 'kredit_position', 'kredit_gewinn')
                else:
                    daten_klassisch = np.array([np.transpose(process),np.transpose(signal), np.transpose(possible), np.transpose(position),np.transpose(cash), np.transpose(golden)])
                    column = ('Prozess (bzw. Buy and Hold)', 'Signal', 'Kauf-Möglich?', 'Position', 'Cash-Bestand','Trading-Position')
                daten_klassisch_transpose = np.transpose(daten_klassisch)
                index_klassisch = ['Vergleich höherer Schlusskurs (Häufigkeit):', 'Vergleich höherer Schlusskurs (kummuliert in €):']
                df3 = pd.DataFrame(data = daten_klassisch_transpose, 
                #index = index_klassisch, 
                columns = column)
                csv_klassisch = df3.to_csv().encode('utf-8')
           
 ######           print(str(process[259]) + " | " + str(golden[259]))
                endwerte_sim[i][0] = process[handelstage_gesamt-1] # Buy and Hold
                endwerte_sim[i][1] = golden[handelstage_gesamt-1]  # Trading
                endwerte_sim_ohne[i][0] = process[handelstage_gesamt-1] # Buy and Hold
                endwerte_sim_ohne[i][1] = golden[handelstage_gesamt-1]  # Trading
                
                endwerte_sim_trading[i] = process[handelstage_gesamt-1]
                endwerte_sim_buyandhold[i] = golden[handelstage_gesamt-1]  

                betragBH += round(process[handelstage_gesamt-1],2)
                betragTS += round(golden[handelstage_gesamt-1],2)
                #betragBH_rund = round(betragBH,2)
                #betragTS_rund = round(betragTS,2)
                
                

                if golden[handelstage_gesamt-1] > process[handelstage_gesamt-1]:
                    #countTS = countTS +1
                    ergebnis_array[0][1] = ergebnis_array[0][1] + 1
                else:
                    #countBH = countBH +1
                    ergebnis_array[0][0] = ergebnis_array[0][0] + 1
               




            ### Ende For Loop alle Simulationen durch ###   
            ### Ab hier: Auswertung der Ergebnisse ###

            print("Trading: " + str(countTS) + " | Buy_And_Hold: " + str(countBH))
            output = "Trading: " + str(countTS) + " | Buy_And_Hold: " + str(countBH)
            #original_title = '<p style="font-family:Courier; color:Blue; font-size: 20px;">Überschrift</p>'
            #st.markdown(original_title, unsafe_allow_html=True)
            #ergebnis_text = "Trading: " + str(countTS) + " | Buy_And_Hold: " + str(countBH)
            #ergebnis_placeholder.text_area("Ergebnis: ",ergebnis_text, height = 50)
            #ergebnis_placeholder.text("Ergebnis: " + ergebnis_text)
            #ergebnis_placeholder.text("Ergebnis: " + ergebnis_text)
            quotient = ergebnis_array[1][1]/ergebnis_array[1][0]
            quotient_leverage = ergebnis_array_kredit[1][1]/ergebnis_array[1][0]

#Häufigkeiten
            ergebnis_array[0][2] = (ergebnis_array[0][0]/anzahl_simulationen)*100 # Häufigkeit relativ BH
            ergebnis_array[0][3] = 100 - ergebnis_array[0][2] # Häufigkeit relativ TS
            ergebnis_array_kredit[0][2] = (ergebnis_array_kredit[0][0]/anzahl_simulationen)*100 # Häufigkeit relativ BH
            ergebnis_array_kredit[0][3] = 100 - ergebnis_array_kredit[0][2] # Häufigkeit relativ TS

            
#Betrag
            ergebnis_array[1][0] = round(betragBH,2)
            ergebnis_array[1][1] = round(betragTS,2)
            ergebnis_array[1][3] = round(quotient*100,2) #relativ Betrag TS gegenüber 100% bzw. BH
            ergebnis_array[1][2] = round(100,2) # relativ BH (Benchmark mit 100%)
            ergebnis_array_kredit[1][0] = ergebnis_array[1][0] # Betrag BH (gleich wie bei ohne Kredit)
            ergebnis_array_kredit[1][3] = round(quotient_leverage*100,2) #relativ Betrag TS mit Kredit gegenüber 100% bzw. BH
            ergebnis_array_kredit[1][2] = round(100,2) # relativ BH mit Kredit (Benchmark mit 100%)

            if quotient >= 1:
                #relative_performance = round((1-(quotient))*100 ,2)
                ergebnis_array[1][4] = round((1-(quotient))*100 ,2) #TS >100% bzw.>BH
            else:
                #relative_performance = round((1-(quotient))*-100 ,2)
                ergebnis_array[1][4] = round((1-(quotient))*100 ,2)

            if quotient_leverage >= 1:
                ergebnis_array_kredit[1][4] = round((1-(quotient_leverage))*100 ,2)
            else:
                ergebnis_array_kredit[1][4] = round((1-(quotient_leverage))*-100 ,2)
            
            #betrag_kredit_gewinn_all_rund = round(betrag_kredit_gewinn_all,2)
            ergebnis_array_kredit[2][1] = round(betrag_kredit_gewinn_all,2)
            #st.success("Vergleich höherer Schlusskurs (Häufigkeit) --> Trading: " + str(countTS) + "  |  Buy_And_Hold: " + str(countBH))
            #st.success("Vergleich höherer Schlusskurs (kummuliert) --> Trading: " + str(betragTS_rund) + "  |  Buy_And_Hold: " + str(betragBH_rund))


### Ergebnisse präsentieren ###
            output = '<p style="font-family:sans-serif; color:black; font-size: 18px;"><i>Simulations-Ergebnisse:</i></p>'
            st.markdown(output, unsafe_allow_html=True)

            
            
                



### Ergebnisse ###
# ohne Kredit ergebnis_array
#[0][0-1] absolute Häufigkeit, 2  600 vs 400
#[0][2-3] relative Häufigkeit, 2  60% vs 40%
#[0][4] Performance Ts gegen BH,  -33,3%
#[1][0-1] absolute Summe der Schlusskurse, 2 15.000 vs 14.000
#[1][2-3] relative Summe der Schlusskurse, 2  100% vs 96%
#[1][4] Performance Ts gegen BH,  -4%

# mit Kredit ergebnis_array_kredit
#[0][0-1] absolute Häufigkeit, 2  550 vs 450
#[0][2-3] relative Häufigkeit, 2  55% vs 45%
#[0][4] Performance Ts gegen BH,  -25,0%
#[1][0-1] absolute Summe der Schlusskurse, 2 15.000 vs 14.500
#[1][2-3] relative Summe der Schlusskurse, 2  100% vs 97,5%
#[1][4] Performance Ts gegen BH,  -2,5%
#[2][0] 0 Gewinn nur mit Kredit (BH)
#[2][1] Gewinn nur mit Kredit (TS)

### check ###

# Vorschläge Performance Messung:
# Grunddaten nochmal auflisten, mu, vola und exp(St)...
# Nur für B&H Wahrscheinlichkeit S>St siehe Trading_Idea Excel
# Median und Durschnitts Kurs --> Kurse addieren und durch Anzahl Sims teilen
# durchschnittliche Gesamtrendite pro Simulation, 2x2 --> 20% vs 18% ((S(T)-S(0))/S(0) pro Sim. und dann den Durchschnitt oder umgekehrt)
# durchschnittliche Jahresrendite pro Simulation, 2x2 -||-

# Distance to B&H --> Wie groß ist der Kursunterschied am Ende einer jeden Sim. --> viele kleine Diffs oder wenige Große? --> evtl. als Balkendiagramm abbilden, z.B. >20, 10<20, <10...
# Vergleich der Max und Min werte, sprich höchste und niedrigster Kurs jeweils von allen Sim's

# Thema Statistische Signifikanz --> bezogen auf Anzahl an Simulationen
# Calmar Ratio --> Bei Trading dann nur die Tage in denen man investiert ist einbeziehen
# Maybe sharpe Ratio






            if kredit_true:
                daten = np.array([[ergebnis_array[0][0], ergebnis_array[0][1]],[ergebnis_array_kredit[0][0], ergebnis_array_kredit[0][1]], [ergebnis_array[1][0], ergebnis_array[1][1]],[ergebnis_array[1][0],ergebnis_array_kredit[1][1] ], [0,ergebnis_array_kredit[2][1]]])
                index_values = ['Vergleich: jeweils höherer Schlusskurs (Häufigkeit)','Vergleich: jeweils höherer Schlusskurs inkl. Leverage (Häufigkeit)', 'Vergleich: Schlusskurse (kummuliert)', 'Vergleich: Schlusskurse inkl. Leverage (kummuliert)', "Gewinn durch Leverage/Kredit"]
                chart_data2 = pd.DataFrame(
                    data = np.array(endwerte_sim),
                    columns=["Buy and Hold", "Trading", "Kredit_Gewinn"],)
                col1, col2, col3, = st.columns(3)
                col1.metric("Buy and Hold (Benchmark)", str(ergebnis_array[1][0]))
                col2.metric("Trading", str(ergebnis_array[1][1]), str(ergebnis_array[1][4])+"% (vs. Buy & Hold)")
                col3.metric("Trading inkl. Kredit-Gewinn", str(round(ergebnis_array_kredit[1][1],2)), str(ergebnis_array_kredit[1][4])+"% (vs. Buy & Hold)")
                
### TODO ###
                #Ergebnistabelle mit Kredit    
                endwerte_sim_leverage = np.zeros(shape=(int(anzahl_simulationen),6)) # 4096,12
                for g in range(len(endwerte_sim_leverage)):
                    endwerte_sim_leverage[g][0] = endwerte_sim[g][0]
                    endwerte_sim_leverage[g][1] = endwerte_sim[g][1]
                    endwerte_sim_leverage[g][2] = endwerte_sim[g][2]
                    endwerte_sim_leverage[g][3] = endwerte_sim_leverage[g][1] + endwerte_sim_leverage[g][2] 
                    endwerte_quotient = (endwerte_sim_leverage[g][1]/endwerte_sim_leverage[g][0]) 
                    endwerte_quotient_leverage = (endwerte_sim_leverage[g][3]/endwerte_sim_leverage[g][0]) 
                    if endwerte_quotient >= 1:
                        relative_performance_alle = round((1-(endwerte_quotient))*-100 ,2)
                    else:
                        relative_performance_alle = round((1-(endwerte_quotient))*-100 ,2)
                    if endwerte_quotient_leverage >= 1:
                        relative_performance_alle_leverage = round((1-(endwerte_quotient_leverage))*-100 ,2)
                    else:
                        relative_performance_alle_leverage = round((1-(endwerte_quotient_leverage))*-100 ,2)
                    endwerte_sim_leverage[g][4] = relative_performance_alle
                    endwerte_sim_leverage[g][5] = relative_performance_alle_leverage

                df_gesamt = pd.DataFrame(data = endwerte_sim_leverage, 
                    #index = index_values, 
                    columns = ('Buy and Hold', 'Trading', "Leverage (Gewinn durch Kredit)", "Trading (inkl. Leverage)", "Trading Performance (gegenüber Benchmark)","Trading Performance inkl. Leverage (gegenüber Benchmark)"))

            else: 
                daten = np.array([[ergebnis_array[0][0], ergebnis_array[0][1]], [ergebnis_array[1][0], ergebnis_array[1][1]]])
                index_values = ['Vergleich: jeweils höherer Schlusskurs (Häufigkeit)', 'Vergleich: Schlusskurse (kummuliert)']
                endwerte_sim_ohne_performance = np.zeros(shape=(int(anzahl_simulationen),3)) # 4096,12
                for g in range(len(endwerte_sim_ohne_performance)):
                    endwerte_sim_ohne_performance[g][0] = endwerte_sim_ohne[g][0]
                    endwerte_sim_ohne_performance[g][1] = endwerte_sim_ohne[g][1]
                     
                    endwerte_quotient = (endwerte_sim_ohne[g][1]/endwerte_sim_ohne[g][0]) 
                    if endwerte_quotient >= 1:
                        endwerte_sim_ohne_performance_alle = round((1-(endwerte_quotient))*-100 ,2)
                    else:
                        endwerte_sim_ohne_performance_alle = round((1-(endwerte_quotient))*-100 ,2)
                   
                    endwerte_sim_ohne_performance[g][2] = endwerte_sim_ohne_performance_alle
   
                chart_data2 = pd.DataFrame(
                    data = np.array(endwerte_sim_ohne),
                    columns=["Buy and Hold", "Trading"],)
                col1, col2, = st.columns(2)
                col1.metric("Buy and Hold (Benchmark)", str(ergebnis_array[1][0]))
                col2.metric("Trading", str(ergebnis_array[1][1]), str(ergebnis_array[1][4])+"% (vs. Buy & Hold)")

                df_gesamt = pd.DataFrame(data = endwerte_sim_ohne_performance, 
                    #index = index_values, 
                    columns = ('Buy and Hold', 'Trading', 'Trading Performance (gegenüber Benchmark)'))



            with st.expander("Ergebnisse als Tabelle"):
                #Auflistung der Gesamtergebnisse
                df = pd.DataFrame(data = daten, 
                    index = index_values, 
                    columns = ('Buy and Hold', 'Trading'))
                df.round(2)
                st.dataframe(df.style.format(subset=['Buy and Hold', 'Trading'], formatter="{:.2f}"))

                st.markdown("***")

                #Auflistung der einzelnen Simulationsergebnisse
                df_gesamt.round(2)
                st.dataframe(df_gesamt)#.style.format(subset=['Buy and Hold', 'Trading'], formatter="{:.2f}"))
            
            
                #index= ('Buy and Hold', 'Trading'))

            # Add histogram data
            # Group data together
            #hist_data = [endwerte_sim_trading, endwerte_sim_buyandhold]
            #group_labels = ['Group 1', 'Group 2']
            # Create distplot with custom bin_size
            #fig = ff.create_distplot(
            #        hist_data, group_labels, bin_size=[.5, .5])

            #st.plotly_chart(fig, use_container_width=True)
            #st.dataframe(df.style.format("{:.2%}"))
            #st.table(df)
            with st.expander("Ergebnisse als Charts"):
                erklaerung_bar = '<p style="font-family:sans-serif; color:black; font-size: 18px;"><i>Bar-Chart: Vergleich "Trading vs. Buy and Hold" je Simulationslauf</i></p>'
                st.markdown(erklaerung_bar, unsafe_allow_html=True)
                st.bar_chart(chart_data2)
                erklaerung_area = '<p style="font-family:sans-serif; color:black; font-size: 18px;"><i>Area-Chart: Vergleich "Trading vs. Buy and Hold" je Simulationslauf</i></p>'
                st.markdown(erklaerung_area, unsafe_allow_html=True)
                st.area_chart(chart_data2)
                erklaerung_line = '<p style="font-family:sans-serif; color:black; font-size: 18px;"><i>Line-Chart: Vergleich "Trading vs. Buy and Hold" je Simulationslauf</i></p>'
                st.markdown(erklaerung_line, unsafe_allow_html=True)
                st.line_chart(chart_data2)
           
            with st.expander("Downloads "):
                            st.download_button(
                                "Verlauf der allerletzten Simulation als CSV/Excel herunterladen (Zweck: Veranschaulichung der Simulation)",
                                csv_klassisch,
                                "file.csv",
                                "text/csv",
                                key='download-csv'
                                )




















### Diskrete Approximation ###
    
    #st.markdown("***")
    st.markdown("")
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
    diskret = '<p style="font-family:sans-serif; color:black; font-size: 30px;"><i>Simulation - Diskret (abzählbar)</i></p>'
    st.markdown(diskret, unsafe_allow_html=True)
    #anzahl_basis = st.number_input('Basis T (Anzahl Bewegungen, Quartalsweise, Monatsweise...)', 1, 20, value=12)
    #start_kapital = st.number_input('Startkapital (in €)', 1, 10000, value=50)

    left_input, right_input = st.columns(2)
    with left_input:
        anzahl_basis = st.number_input('Basis T (Anzahl Bewegungen, 4=Quartalsweise, 12=Monatsweise...)', 1, 20, value=12)
        anzahl_down = st.number_input('Kaufen bei X Abwärtsbewegungen hintereinander', 0, 12)
    with right_input:
        start_kapital = st.number_input('Startkapital (in €)', 1, 10000, value=50)
        anzahl_up = st.number_input('Verkaufen bei X Aufwärtsbewegungen hintereinander',0,12)

    basis = 1/(anzahl_basis) #12
    startKapital = start_kapital
    
    if st.button('Simulation durchführen (diskret)'):
        with st.spinner('Bitte warten...'):
            laenge = np.power(2,anzahl_basis)
            print(laenge)
            verlaufArray = np.zeros(shape=(laenge,anzahl_basis)) # 4096,12
            ergebnis_array_diskret = np.zeros(shape=(laenge,2)) # 4096
            #st.write("""
            #*Button klicken zum ausführen der Simulation*
            #""")

            a = np.zeros(shape=(laenge,anzahl_basis)) #4096, 12
            b = ["0"]*12           

            for t in range(laenge): #4096
                x = str(binary(t))
                #print(x)
                #print(t)
                for index, letter in enumerate(x):
                    if letter == "0":
                        a[t][index] = 0 
                        #c[t][index] = 'down'
                    else:
                        a[t][index] = 1
                        #c[t][index] = 'up'
                    #print(index, letter)
                #print(c[t])
                
            #print(a)

            up = kursentwicklung_up(sigma, basis)
            down = kursentwicklung_down(sigma, basis)

            #print(laenge)

            for t in range(laenge): #4096
                x = str(binary(t))
                for index, letter in enumerate(x):
                    if letter == "0":
                        a[t][index] = 0 
                    else:
                        a[t][index] = 1
            #print(a)

            # alle Kurse (4096 x 12) zu jedem Zeitpunkt berechnen
            endwerte = [0.0] * laenge #4096
            for t in range(laenge): #4096
                for d in range(anzahl_basis): #12
                    if a[t][d] == 0:
                        if d == 0:
                            verlaufArray[t][d] = startKapital * down 
                        else:
                            verlaufArray[t][d] = verlaufArray[t][d-1] * down 
                    else:
                        if d == 0:
                            verlaufArray[t][d] = startKapital * up 
                        else:
                            verlaufArray[t][d] = verlaufArray[t][d-1] * up 
                endwerte[t] = round(verlaufArray[t][anzahl_basis-1], 2)  # 11, 2  Hier muss gerundet werden, evtl. schon früher da sonst mehr als 12 Entwerte herauskommen
            moegliche_endwerte = list(dict.fromkeys(endwerte, 2))

            for z in range(laenge): #4096
                comp = algoTrading(a[z], verlaufArray[z], anzahl_up, anzahl_down, anzahl_basis, start_kapital)
                ergebnis_array_diskret[z][0] = comp
                ergebnis_array_diskret[z][0] = endwerte[z]
                summe_buyAndHold_diskret += endwerte[z]
                summe_trading_diskret += comp
                if comp > endwerte[z]:
                    counter_trading_diskret += 1
                if comp < endwerte[z]:
                    counter_buyAndHold_diskret += 1
                if comp == endwerte[z]:
                    counter_indifferent_diskret += 1
                    summe_indifferent_diskret += comp
                print("Vergleich: " + str(comp) + " vs. " + str(endwerte[z]))
            
            #print("a: " + str(a[500]) + "  verlauf: " + str(verlaufArray[500]) + "  endwerte: " + str(endwerte[500]))
            #st.success('Done!' + " --> Ergebnis: " + str(up) + " | " + str(down))
            #st.write("Anzahl der Möglichkeiten für die Endwerte: " + str(moegliche_endwerte))
            #st.write("Up: " + str(up))
            #st.write("Down: " + str(down))
            #st.write("Diskret Häufigkeit --> Trading: " + str(counter_trading_diskret) + " Buy and Hold: " + str(counter_buyAndHold_diskret) + " Indifferent: " + str(counter_indifferent_diskret))
            #st.write("Diskret Summe-Kapital --> Trading: " + str(round(summe_trading_diskret,2)) + " Buy and Hold: " + str(round(summe_buyAndHold_diskret,2)) + " Indifferent: " + str(round(summe_indifferent_diskret,2)))
            #st.write(a)
            daten_diskret = np.array([[counter_buyAndHold_diskret, counter_trading_diskret], [summe_buyAndHold_diskret, summe_trading_diskret]])
            index_values2 = ['Vergleich höherer Schlusskurs (Häufigkeit):', 'Vergleich höherer Schlusskurs (kummuliert in €):']
            df2 = pd.DataFrame(data = daten_diskret, 
                index = index_values2, 
                columns = ('Buy and Hold', 'Trading'))
            df2.round(2)
            output = '<p style="font-family:sans-serif; color:black; font-size: 18px;"><i>Ergebnis:</i></p>'
            spalte_1, spalte_2 = st.columns(2)
            chart_data = pd.DataFrame(
            data = np.array([summe_buyAndHold_diskret, summe_trading_diskret]),
            columns=["kummulierte Schlusskurse"],
            index= ('Buy and Hold', 'Trading'))
   
           # csv = df2.to_excel("output.xlsx")
            #df2.to_csv().encode('utf-8')
            csv = df2.to_csv().encode('utf-8')

            #c = alt.Chart(chart_data).mark_bar()
            #st.altair_chart(c, use_container_width=True)

            with spalte_1:
                st.markdown(output, unsafe_allow_html=True)
                st.dataframe(df2.style.format(subset=['Buy and Hold', 'Trading'], formatter="{:.2f}"))
                st.download_button("Ergebnis als CSV/Excel herunterladen",csv,"file.csv","text/csv",key='download-csv')
            with spalte_2:
                st.bar_chart(chart_data)
                #st.markdown(get_table_download_link(df2), unsafe_allow_html=True)
               
     

#def get_table_download_link(df):
#    #Generates a link allowing the data in a given panda dataframe to be downloaded
#    #in:  dataframe
#    #out: href string
#    csv = df.to_excel("output.xlsx")
#    #b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
#    href = f'<a href="data:file/xlsx;base64,{csv}">Download csv file</a>'
#    return href


def kursentwicklung_up(sigma, basis):
    up_1 = np.exp(sigma * np.sqrt(basis))
    print(up_1)
    return up_1


def kursentwicklung_down(sigma, basis):
    down_1 = np.exp(-sigma * np.sqrt(basis))
    print(down_1)
    return down_1

def algoTrading(array1, kurs, ups, downs, anzahl_basis2, start_kapital): # 6 - 0
    #strategie = 3
    strategie_ups = ups
    strategie_downs = downs
    kapital = start_kapital #50.00 # entweder realitätsnah, indem Aktien stückelbar sind und gewinne reinvestiert werden oder man nimmt den profit/verlust immer raus und kuaft/verkauft zu dem kurs, egal wie viel gesamtkapital man hat
    anteil = 1.0
    market_in = False 
    if strategie_ups == 0 and strategie_downs == 0: # D.h. immer direkt Verkaufen und Kaufen --> 50€ 
        return round(kapital,2)

    for u in range((anzahl_basis2)): # 12
        trading_buy = True
        trading_sell = True

        # For downs --> wann kaufen  
        if u >= strategie_downs-1:
            for e in range(strategie_downs):
                if array1[u - e] == 1:
                    trading_buy = False
            if trading_buy and not market_in:
                # buy
                anteil = kapital/kurs[u]
                market_in = True

        # For ups --> wann verkaufen
        if u >= strategie_ups-1:
            for e in range(strategie_ups):
                if array1[u - e] == 0:
                    trading_sell = False
            if trading_sell and market_in:
                # sell
                market_in = False
                #kapital = kurs[u]

        if market_in:  # Platzierung evtl. oberhalb sinnvoller?
            kapital = anteil * kurs[u]

          # if u >= strategie-1:  # Old Stuff bei einer Strategie (parralell up/down)
          #      trading_buy = True
          #  trading_sell = True
          #  for e in range(strategie):
          #      if array1[u - e] == 1:
          #          trading_buy = False
          #      if array1[u - e] == 0:
          #          trading_sell = False
          #  if trading_buy and not market_in:
          #    # buy
          #      anteil = kapital/kurs[u]
           #     market_in = True
           # if trading_sell and market_in:
           #     # sell
           #     market_in = False
           #     #kapital = kurs[u]

    #print(kapital)
    return round(kapital,2) #ergebnis


if __name__ == "__main__":
    main()