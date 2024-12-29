from django.shortcuts import render
from django.http import JsonResponse
import numpy as np
import geopandas as gpd
import folium

def atualizar_candidatos_por_ano(ano):
   """
    Retorna os candidatos disponíveis com base no ano selecionado.
    """
   if ano == "2024":
        return [
            {'nome': "CORRINHA", 'cor': '#c4122d', 'imagem_url': '/static/mapa/images/corrinha.jpg'},
            {'nome': "DRA LIVIA", 'cor': '#FFCC00', 'imagem_url': '/static/mapa/images/livia.jpg'},
            {'nome': "EDUARDO XI", 'cor': '#0067A5', 'imagem_url': '/static/mapa/images/eduardo.jpeg'},
        ]
   elif ano == "2020":
        return [
            {'nome': "JOSE AUGUS", 'cor': '#005533', 'imagem_url': '/static/mapa/images/jose_augusto_2020.jpg'},
            {'nome': "DRA LIVIA", 'cor': '#FE8E6D', 'imagem_url': '/static/mapa/images/livia_2020.jpeg'},
        ]
   elif ano=="2016":
       return[
            {'nome': "JOSE AUGUS", 'cor': '#009AE2', 'imagem_url': '/static/mapa/images/jose_augusto_2016.jpg'},
            {'nome': "MARFISA", 'cor': '#FE8E6D', 'imagem_url': '/static/mapa/images/marfisa_2016.jpg'},]

   elif ano=="2012":
       return[
            {'nome': "TORRES NET", 'cor': '#0080FF', 'imagem_url': '/static/mapa/images/torres_neto.png'},
            {'nome': "MARFISA", 'cor': '#FFCC00', 'imagem_url': '/static/mapa/images/marfisa_2012.png'},]
       
   elif ano=="2008":
       return[
            {'nome': "TORRIM", 'cor': '#0080FF', 'imagem_url': '/static/mapa/images/torrim_2008.png'},
            {'nome': "MARCOS MAR", 'cor': '#FFCC00', 'imagem_url': '/static/mapa/images/marcos_marques_2008.png'},]
       
   elif ano=="2004":
       return[
            {'nome': "MARCOS MAR", 'cor': '#0080FF', 'imagem_url': '/static/mapa/images/marcos_marques_2004.png'},
            {'nome': "JOSE FLAVI", 'cor': '#c4122d', 'imagem_url': '/static/mapa/images/jose_flavio.png'},]
   elif ano=="2000":
       return[
            {'nome': "TORRIM", 'cor': '#0080FF', 'imagem_url': '/static/mapa/images/torrim_2000.png'},
            {'nome': "ENOQUE MOR", 'cor': '#ec008c', 'imagem_url': '/static/mapa/images/enoque_2000.png'},]
   return []

def carregar_geojson_por_ano(ano):
    """
    Carrega o arquivo GeoJSON correspondente ao ano.
    """
    arquivo_geojson = f'mapa/static/mapa/dados_votacao_pf_{ano}.geojson'
    try:
        return gpd.read_file(arquivo_geojson), None
    except FileNotFoundError:
        return None, {'error': f"Arquivo para o ano {ano} não encontrado."}

def nome_candidato(name_candidate, colunas):
    if name_candidate is None:
        return None

    # Normaliza o nome recebido e os nomes nas colunas
    name_candidate = name_candidate.lower().strip()
    for nome in colunas:
        nome_limpo = nome.lower().strip()
        # Verifica se o nome do candidato é parte de qualquer nome das colunas
        if name_candidate in nome_limpo or nome_limpo in name_candidate:
            return nome
    return None


def cor_bairro(dado, colunas_porcentagem, colunas, year):
        maior_percentual = 0
        cor = 'white'
        for col in colunas_porcentagem:
            valor = safe_float_conversion(dado[col])
            if valor > maior_percentual:
                maior_percentual = valor
                name = f"Partido_{nome_candidato(col.replace('Perc_', '').upper(), colunas).upper()}";
                print("nome: ",name)
                for j in range(len(colunas)):
                    if(colunas[j] == name[:len(colunas[j] )]):
                         partido = dado.get(colunas[j],0)
                cor = cor_partido(partido);
        return cor  

def cor_partido(partido):
    cores = {
        'PT':'#c4122d',
        'PSB':'#FFCC00',
        'PP': '#0067A5',
        'PDT': '#FE8E6D',
        'PTB':'#005533',
        'PSD': '#FFA500',
        'PPS':'#ec008c',
        'PSDB':'#0080FF'
    }
    return cores.get(partido, "Candidato não encontrado")
    
def safe_float_conversion(value):
        if isinstance(value, str):
            try:
                return float(value.replace(',', '.'))
            except ValueError:
                return None
        return value
          
def atualizar_mapa(request):
        
    # Obter o candidato e o ano
    candidato = request.GET.get('candidato', None)
    ano = request.GET.get('ano', '2024')
    
    # Atualizar candidatos
    candidatos_disponiveis = atualizar_candidatos_por_ano(ano)
    nomes_candidatos = [c['nome'] for c in candidatos_disponiveis]
    

    if not candidatos_disponiveis:
        return JsonResponse({'error': f"Nenhum candidato encontrado para o ano {ano}."}, status=404)


    # Carregar dados GeoJSON
    gdf, erro = carregar_geojson_por_ano(ano)
    if erro:
        return JsonResponse(erro, status=404)

    colunas = gdf.columns.tolist()
    colunas_porcentagem = [col for col in colunas if col.startswith('Perc_')]
    
    candidato = nome_candidato(candidato, colunas);
   
    if candidato is None:
        candidato = nome_candidato(nomes_candidatos[0], colunas)
    elif candidato not in nomes_candidatos:
        return JsonResponse({'error': f"Candidato {candidato} não encontrado para o ano {ano}."}, status=404)
    
    # Criar o mapa
    mapa_pf = folium.Map(location=[-4.241, -40.636], zoom_start=12)

    for i, dado in gdf.iterrows():
        bairro = dado['Endereço']
        name = f"Partido_{candidato.upper()}"
        for j in range(len(colunas)):
            if(colunas[j] == name[:len(colunas[j] )]):
                partido = colunas[j];
        print('Partido: '+partido)
        cor = cor_bairro(dado, colunas_porcentagem.copy(), colunas.copy(), ano)
        # Recuperar o percentual do candidato no bairro atual
        coluna_percentual = nome_candidato(f"Perc_{candidato.upper()}", colunas) 
        voto_cand = safe_float_conversion(dado.get(coluna_percentual, 0))
        tot = safe_float_conversion(dado.get('Total_voto', 0))
        percentual = (voto_cand/tot)*100;
        percentual_formatado = f"{percentual:.2f}%" if percentual else "0%"
        folium.GeoJson(
            gdf.iloc[i:i+1],
            style_function=lambda feature, color=cor: {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 2
            },
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Endereço', 'Local de V',coluna_percentual,partido],  # Inclua apenas campos que você precisa
            aliases=[
                'Endereço:', 
                'Local de Votação:',
                f'{candidato} ({percentual_formatado}):',
                "Partido: "
            ],
            localize=True,
            sticky=True,
        ),
            highlight_function=lambda feature,color=cor: {
                'color': 'black',
                'weight': 5,
                'fillOpacity': 0.5,
                'fillColor': color
            },
        popup=folium.Popup(
            f"<b>Bairro:</b> {bairro}<br>"
            f"<b>Candidato:</b> {candidato}<br>"
            f"<b>Percentual:</b> {percentual_formatado}",
            
            max_width=300
        )
        ).add_to(mapa_pf)

    mapa_html = mapa_pf._repr_html_()

    # Retorno AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'mapa_html': mapa_html, 'candidatos': candidatos_disponiveis, 'ano': ano, 'candidato_selecionado': candidato})
    
    return render(request, 'mapa/mapa.html', {'mapa_html': mapa_html, 'candidato': candidato, 'ano': ano})

