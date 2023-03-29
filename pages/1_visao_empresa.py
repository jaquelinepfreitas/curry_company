#libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

#aumentar largura das páginas
st.set_page_config(page_title='Visão Empresa', layout = 'wide')

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

def order_metric(df1):
    df_aux = df1.loc[: ,['ID','Order_Date']].groupby(['Order_Date']).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
    fig = px.bar(df_aux, x = 'order_date', y = 'qtde_entregas')
    return fig

def traffic_order_share (df1):
    df_aux2 = df1.loc[:, ['ID','Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
    df_aux2['Delivery_percentage_traffic'] = df_aux2['ID']/df_aux2['ID'].sum()
    fig=px.pie(df_aux2, values = 'Delivery_percentage_traffic', names = 'Road_traffic_density')
    return fig
            
def traffic_order_city(df1):
    df_aux3= df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig= px.scatter(df_aux3, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig 

def order_by_week (df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    fig = px.line(df_aux1, x = 'week_of_year', y = 'ID' )
    return fig

def order_share_by_week (df1):
    df_aux4 = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux5 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
    df_aux6 = pd.merge(df_aux4, df_aux5, how= 'inner')
    df_aux6['order_by_delivery'] = df_aux6['ID'] / df_aux6 ['Delivery_person_ID']
    fig =px.line( df_aux6, x='week_of_year', y='order_by_delivery' )
    return fig

def country_maps (df1):
    df_aux7 = df1.loc[:, ['Delivery_location_latitude','Delivery_location_longitude', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    map = folium.Map ( zoom_start=11 )
    for index, location_info in df_aux7.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static(map, width=1024 ,height=600)
    return None
#====================================================
#-------Inicio da estrutura logica do codigo---------
#====================================================

#import dataset
df = pd.read_csv('train.csv') 

#copy csv
df1 = df.copy()

#limpeza dos dados
df1 = clean_code(df1)

#==============================
#------- Barra lateral---------
#==============================
st.markdown('# Marketplace - Visão Cliente')

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

st.sidebar.markdown('### Powered by Comunidade DS')

#filtro data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#st.dataframe(df1)

#==============================
#------Layout streamlit--------
#==============================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão tática', 'Visão geográfica'])

#PRIMEIRA PAGINA
with tab1:
    
    #PRIMEIRO CONTAINER
    with st.container():
        st.markdown('## Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True) 
        
    #SEGUNDO CONTAINER
    with st.container():
        col1, col2 = st.columns(2)
        
        #PRIMEIRA COLUNA SEGUNDO CONTAINER
        with col1:
            fig = traffic_order_share(df1)
            st.markdown('## Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)

        #SEGUNDA COLUNA SEGUNDO CONTAINER
        with col2:
            fig = traffic_order_city(df1)
            st.markdown('## Traffic Order City')
            st.plotly_chart(fig, use_container_width=True)

#SEGUNDA PAGINA
with tab2:
    
    #PRIMEIRO CONTAINER
    with st.container():
        fig = order_by_week(df1)
        st.markdown('## Order by Week')
        st.plotly_chart(fig, use_container_width=True)
        
    #SEGUNDO CONTAINER
    with st.container():
        fig = order_share_by_week (df1)
        st.markdown('## Order Share by Week')
        st.plotly_chart(fig, use_container_width=True)

#TERCEIRA PAGINA
with tab3:
    st.markdown('## Country Map')
    country_maps (df1)