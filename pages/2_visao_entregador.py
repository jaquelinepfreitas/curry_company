#libraries
import pandas as pd
#import plotly.express as px
#import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image
#import folium
#from streamlit_folium import folium_static

#aumentar largura das páginas
st.set_page_config(page_title='Visão Entregador', layout = 'wide')

#==============================
#----------Funcoes-------------
#==============================
def clean_code(df1):
    """ Esta funcao tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remocao dos dados NaN
        2. Mudanca do tipo de coluna de dados
        3. Remocao dos espacos das variaveis de texto
        4. Formatacao da coluna de datas
        5. Limpeza da coluna tempo (remocao do texto da variavel numerica)
        
        Input: Dataframe
        Output: Dataframe  
    """
    
    df1.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]
    df1 = df1.loc[df1['City'] != 'NaN', :]
    df1 = df1.loc[df1['Delivery_person_Age'] != 'NaN ', :]
    df1 = df1.loc[df1['multiple_deliveries'] != 'NaN ', :]
    df1 = df1.loc[df1['Festival'] != 'NaN', :]
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    df1['Time_taken(min)']= df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )
    return df1

def top_delivers (df1, top_asc): 
    df_aux16= df1.loc[:, ['Time_taken(min)', 'Delivery_person_ID', 'City']].groupby(['City','Delivery_person_ID']).max().sort_values(['City','Time_taken(min)'], ascending= top_asc).reset_index()
    df_aux17 = df_aux16.loc[df_aux16['City'] == 'Metropolitian',:].head(10)
    df_aux18 = df_aux16.loc[df_aux16['City'] == 'Urban',:].head(10)
    df_aux19 = df_aux16.loc[df_aux16['City'] == 'Semi-Urban',:].head(10)

    df_aux = pd.concat([df_aux17, df_aux18, df_aux19]).reset_index(drop = True)
    return df_aux

#=================================================
#-------Inicio da estrutura logica do codigo------
#=================================================
#import dataset
df = pd.read_csv('train.csv') 

#copy csv
df1 = df.copy()

#limpeza dos dados
df1 = clean_code(df1)

#==============================
#------- Barra lateral---------
#==============================
st.markdown('# Marketplace - Visão Entregador')

image_path = 'vetor.jpg'

image = Image.open(image_path)
st.sidebar.image(image, width=180)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?', value=pd.datetime(2022,4,13), min_value=pd.datetime(2022,2,11), max_value=pd.datetime(2022,4,6), format='DD-MM-YYYY')
#st.header(variavel)
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito?', ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""")

weather_options = st.sidebar.multiselect('Quais as condições do clima?', ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'], default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])
st.sidebar.markdown("""___""")

st.sidebar.markdown('### Powered by Comunidade DS')

#filtro data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#filtro clima
linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas, :]

#==============================
#------Layout streamlit--------
#==============================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

#PRIMEIRA PAGINA
with tab1:
    
    #PRIMEIRO CONTAINER
    with st.container():
        st.markdown('### Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        
        #PRIMEIRA COLUNA PRIMEIRO CONTAINER
        with col1:
            #st.markdown('### Maior idade:')
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade:', maior_idade)
            
        #SEGUNDA COLUNA PRIMEIRO CONTAINER
        with col2:
            #st.markdown('### Menor idade')
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade:', menor_idade)
            
        #TERCEIRA COLUNA PRIMEIRO CONTAINER
        with col3:
            #st.markdown('### Melhor condição veículo')
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição veículo:', melhor_condicao)
            
        #QUARTA COLUNA PRIMEIRO CONTAINER
        with col4:
            #st.markdown('### Pior condição veículo')
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição veículo:', pior_condicao)
            
    #SEGUNDO CONTAINER
    with st.container():
        st.markdown("""___""")
        st.markdown('### Avaliações')
        col1, col2 = st.columns(2, gap='large')
        
        
        #PRIMEIRA COLUNA SEGUNDO CONTAINER
        with col1:
            st.markdown('###### Avaliação média por entregador:')
            df_aux8 = df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe( df_aux8 )
            
            
        #SEGUNDA COLUNA SEGUNDO CONTAINER
        with col2:
            st.markdown('###### Avaliação média por trânsito:')
            df_aux9 = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings':['mean', 'std']})
            df_aux9.columns = ['delivery_mean', 'delivery_std']
            df_aux9.reset_index()
            st.dataframe(df_aux9)
                    
            st.markdown("""___""")
                    
            st.markdown('###### Avaliação média por condições climáticas:')
            df_aux10 = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean', 'std']})
            df_aux10.columns = ['deliery_mean', 'delivery_std']
            df_aux10.reset_index()
            st.dataframe(df_aux10)
                    
    #TERCEIRO CONTAINER
    with st.container():
        st.markdown("""___""")
        st.markdown('### Velocidade de entrega')
        col1, col2 = st.columns(2, gap='large')
        
        #PRIMEIRA COLUNA TERCEIRO CONTAINER
        with col1:
            st.markdown('###### Top entregadores mais rápidos por cidade:')
            df3 = top_delivers (df1, top_asc = True)
            st.dataframe(df3)
            
        #SEGUNDA COLUNA TERCEIRO CONTAINER
        with col2:
            st.markdown('###### Top entregadores mais lentos por cidade:')
            df3 = top_delivers (df1, top_asc = False)
            st.dataframe(df3)
            
            
            #df_aux11= df1.loc[:, ['Time_taken(min)', 'Delivery_person_ID', 'City']].groupby(['City','Delivery_person_ID']).min().sort_values(['City','Time_taken(min)'], ascending = True).reset_index()
            #df_aux12 = df_aux11.loc[df_aux11['City'] == 'Metropolitian',:].head(10)
            #df_aux13 = df_aux11.loc[df_aux11['City'] == 'Urban',:].head(10)
            #df_aux14 = df_aux11.loc[df_aux11['City'] == 'Semi-Urban',:].head(10)
            #df_aux15 = pd.concat([df_aux12, df_aux13, df_aux14]).reset_index(drop = True)