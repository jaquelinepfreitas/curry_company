#libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image
import numpy  as np
#import folium
#from streamlit_folium import folium_static

#aumentar largura das páginas
st.set_page_config(page_title='Visão Restaurante', layout = 'wide')
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

def distance_column(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols].apply( lambda x:haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),         (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1)
    return df1

def avg_std_time_delivery(df1, op, festival):
    """
        Esta funcao calcula o tempo medio ou o desvio padrao do tempo de entrega.
        Parametros:
        Input:
          -df: Dataframe com os dados necessarios para o calculo
          -op: Tipo de operacao que precisa ser calculado
            'avg_time': calcula o tempo medio
            'std_time': calcula o desvio padrao do tempo de entrega
        Output:
            -df: dataframe com 2 colunas e 1 linha
    """
    df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
                          .groupby( 'Festival' )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round( df_aux.loc[df_aux['Festival'] == festival, op], 2 )
    return df_aux

def avg_std_time_graph(df1):
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure() 
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time']))) 
    fig.update_layout(barmode='group') 
    return fig

def avg_std_time_on_traffic(df1):
    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',color='std_time', color_continuous_scale='Darkmint', color_continuous_midpoint = np.average(df_aux['std_time'] ) )
    return fig
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
st.markdown('# Marketplace - Visão Restaurante')

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
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
            delivery_unique = len( df1.loc[:, 'Delivery_person_ID'].unique() )
            col1.metric( 'Entregadores:', delivery_unique )
            
        with col2:
            df1 = distance_column(df1)
            avg_distance = np.round( df1['distance'].mean(), 2 )
            col2.metric( 'Distância média:', avg_distance )
            
        with col3:
            df_aux = avg_std_time_delivery(df1, 'avg_time', 'Yes')
            col3.metric( 'Tempo Médio em Festivais', df_aux )
            
        with col4:
            df_aux = avg_std_time_delivery(df1, 'std_time', 'Yes')
            col4.metric( 'STD entrega em Festivais', df_aux )
            
        with col5:
            df_aux = avg_std_time_delivery(df1, 'avg_time', 'No')
            col5.metric( 'Tempo Médio', df_aux )
            
        with col6:
            df_aux = avg_std_time_delivery(df1, 'std_time', 'No')
            col6.metric( 'STD entrega', df_aux )
        
    st.markdown("""___""")    
    #SEGUNDO CONTAINER
    with st.container():
        #st.markdown('### 2')
        col1, col2 = st.columns( 2 , gap="large")
        
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart( fig, use_container_width=True )
            
        with col2:
            df_aux = ( df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                          .groupby( ['City', 'Type_of_order'] )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            st.dataframe( df_aux )
            
    st.markdown("""___""")
    #TERCEIRO CONTAINER
    with st.container():
        st.markdown('### Distribuição do Tempo')
        
        col1, col2 = st.columns( 2 )
        with col1:
            df1 = distance_column(df1)
            avg_distance = df1.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
            fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart( fig, use_container_width=True )

        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart( fig, use_container_width=True )