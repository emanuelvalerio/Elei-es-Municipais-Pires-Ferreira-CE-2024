from django.shortcuts import render
from django.http import JsonResponse
import numpy as np
import geopandas as gpd
import folium

def mapa_view(request):
    # Obter o candidato selecionado (ou padrão)
    candidato = request.GET.get('candidato', 'DRA LIVIA')
    print(f"Candidato selecionado: {candidato}")
    # Carregar o GeoJSON
    gdf = gpd.read_file('mapa/static/mapa/dados_votacao_pf_2024.geojson')

    # Função para definir a cor com base no candidato vencedor
    def cor_bairro(porc_corrinha, porc_livia, porc_ximenes):
       if porc_corrinha > 50:
          return 'red'  # Cor para Corrinha
       elif porc_livia > 50:
          return 'yellow'  # Cor para Lívia
       elif porc_ximenes > 50:
          return 'blue'  # Cor para Ximenes
       else:
          return 'white'  # Cor para empate

    # Criar o mapa
    mapa_pf = folium.Map(location=[-4.241, -40.636], zoom_start=12)
    
    # Adicionando cada bairro como um polígono no mapa
    for i, dado in gdf.iterrows():
        bairro = dado['Endereço']
        
        # Função para conversão segura de valores para float
        def safe_float_conversion(value):
            if isinstance(value, str):
                try:
                    return float(value.replace(',', '.'))
                except ValueError:
                    return np.nan  # Lidar com casos de falha na conversão
            return value
        
        # Obtendo as porcentagens e votos
        porc_corrinha = safe_float_conversion(dado['Perc_Corri'])
        porc_livia = safe_float_conversion(dado['Perc_Livia'])
        porc_ximenes = safe_float_conversion(dado['Perc_Ximen'])
        total_votos = safe_float_conversion(dado['Total_voto'])
        
        # Obter a cor para o bairro
        cor = cor_bairro(porc_corrinha, porc_livia, porc_ximenes)

        # Criar o popup com as informações dos votos
        popup = folium.Popup(f"""
        Bairro: {bairro}<br>
        Corrinha: {porc_corrinha:.2f}% ({total_votos * porc_corrinha / 100:.0f} votos)<br>
        Lívia: {porc_livia:.2f}% ({total_votos * porc_livia / 100:.0f} votos)<br>
        Ximenes: {porc_ximenes:.2f}% ({total_votos * porc_ximenes / 100:.0f} votos)
        """, max_width=300)
    
            
        folium.GeoJson(
        gdf,  # Seu GeoDataFrame
        style_function=lambda feature,color=cor: {
            'fillColor': color,  # Cor interna (transparente)
            'color': 'black',  # Cor padrão da borda
            'weight': 1,  # Espessura da borda
            'fillOpacity': 2  # Transparência
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Endereço','Local de V',candidato],  # Colunas que deseja exibir no tooltip
            aliases=['Endereço','Local de Votação','Votos'],  # Rótulos para as colunas
            localize=True
        ),
        highlight_function=lambda feature: {
            'color': 'blue',  # Cor da borda ao clicar
            'weight': 3,  # Espessura da borda ao clicar
            'fillOpacity': 0.3,  # Transparência ao clicar
            'fillColor': 'yellow'  # Cor de preenchimento ao clicar
        }
        ).add_to(mapa_pf)

    # Obter o mapa como um HTML
    mapa_html = mapa_pf._repr_html_()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'mapa_html': mapa_html})

    # Passar o mapa gerado para o contexto
    return render(request, 'mapa/mapa.html', {'candidato': candidato, 'mapa_html': mapa_html})
