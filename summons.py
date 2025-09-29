import streamlit as st
import math
import random
from datetime import datetime
from html import escape
import pandas as pd
import numpy as np
# ---------------------------
# Configuração da página
# ---------------------------
st.set_page_config(page_title="Summons", layout="wide")
nivel = 6
def invocacoes_tab():
    invocacoes = ['Meatshield', 'Spores', 'Thornslinger']

    atributos_invocacoes = {
        "Meatshield": 'atributos_meatshield.csv',
        "Spores": 'atributos_spores.csv',
        "Thornslinger": 'atributos_thornslinger.csv',    
    }

    fotos_invocacoes = {
        "Meatshield": 'meatshield.jpeg',
        "Spores": 'spores.jpeg',
        "Thornslinger": 'thornslinger.jpeg'
    }

    graus_invocacoes = {
        "Meatshield": '4° Grau',
        "Spores": '4° Grau',
        "Thornslinger": '3° Grau'
    }    

    maestrias_invocacoes = {
        "Meatshield": ['Fortitude','Luta'],
        "Spores": ['Reflexo', 'Feitiçaria','Investigação', 'Furtividade'],
        "Thornslinger": ['Luta','Fortitude','Atletismo']    
    }

    especializacao_invocacoes = {
        "Meatshield": [],
        "Spores": ['Feitiçaria','Investigação'],
        "Thornslinger": []            
    }

    CA_inv = {
        "Meatshield": 21,
        "Spores": 17,
        "Thornslinger": 18    
    }

    PV_inv = {
        "Meatshield": 40,
        "Spores": 35,
        "Thornslinger": 50    
    }

    movimento_inv = {
        "Meatshield": '10,5m',
        "Spores": '7,5m',
        "Thornslinger": '7,5m'    
    }

    df_per_inv = pd.read_csv('pericias_invocacoes.csv')

    col_inv1, col_inv2, col_inv3 = st.columns(3)


    with col_inv1:                
            with st.container(border=True):
                st.subheader('Meatshield, invocação de '+str(graus_invocacoes.get('Meatshield')))
                a1, a2 = st.columns([1,2])
                a1.image(fotos_invocacoes.get('Meatshield'))
                a2.write('Meatshield é um corpo amaldiçoado, gerado por Frank a partir da flora local. O nome já diz tudo, esse corpo amaldiçoado tem como sua única missão defender seu invocador e aliados com seu próprio corpo.')
                a2.write('Com uma reação, Meatshield pode entrar na frente de um ataque inimigo dentro de 6 metros. Tomando assim, o dano que seria proferido a seu aliado')
                c1, c2 = st.columns(2)
                c1.metric("PV", PV_inv.get('Meatshield'))
                c1.metric("CA/RD", str(CA_inv.get('Meatshield'))+'/2')
                c2.number_input(label="PV Atual", min_value=0, step=1)
                c2.metric('Movimento', movimento_inv.get('Meatshield'))
                st.markdown('---')
                st.markdown('#### Atributos')
                ai1, ai2 = st.columns(2)

                # Primeira coluna: For, Des, Con
                for _, row in pd.read_csv(atributos_invocacoes.get('Meatshield')).iloc[0:3].iterrows():
                    ai1.write(f"**{row['Atributo']}**: {row['Valor']} ({row['Modificador']:+d})")

                # Segunda coluna: Int, Sab, Car
                for _, row in pd.read_csv(atributos_invocacoes.get('Meatshield')).iloc[3:6].iterrows():
                    ai2.write(f"**{row['Atributo']}**: {row['Valor']} ({row['Modificador']:+d})")
                
                st.markdown('---')
                st.markdown('#### Perícias')

                # --- parâmetros
                half_level = nivel // 2
                maestria_val = math.ceil(1 + nivel / 4)

                # normalizadores
                def norm_attr(x: str) -> str:
                    m = {
                        'FOR': 'For',
                        'DES': 'Des', 'DEX': 'Des',
                        'CON': 'Con',
                        'INT': 'Int',
                        'SAB': 'Sab', 'WIS': 'Sab',
                        'CAR': 'Car', 'CHA': 'Car',
                    }
                    key = str(x).strip().upper()
                    return m.get(key, str(x).strip())

                def norm_pericia(x: str) -> str:
                    return str(x).strip().casefold()

                # sets de maestria/especialização para a invocação selecionada
                maes_set = {norm_pericia(p) for p in (maestrias_invocacoes.get('Meatshield') or [])}
                esp_set = {norm_pericia(p) for p in (especializacao_invocacoes.get('Meatshield') or [])}

                # mapa de modificadores de atributo da invocação
                attr_mod_map = {
                    norm_attr(a): int(m)
                    for a, m in zip(pd.read_csv(atributos_invocacoes.get('Meatshield'))['Atributo'], pd.read_csv(atributos_invocacoes.get('Meatshield'))['Modificador'])
                }

                # df base vem de df_per_inv (Pericia, Atributo)
                per_df = df_per_inv[['Pericia', 'Atributo']].copy()
                per_df['Atributo'] = per_df['Atributo'].apply(norm_attr)

                # modificador do atributo
                per_df['ModAtributo'] = per_df['Atributo'].map(attr_mod_map).fillna(0).astype(int)

                # maestria/especialização por perícia (case-insensitive e tolera plural simples)
                def has_flag(pname_norm: str, flag_set: set) -> bool:
                    return pname_norm in flag_set or (pname_norm.endswith('s') and pname_norm[:-1] in flag_set)

                per_df['_norm'] = per_df['Pericia'].apply(norm_pericia)
                per_df['Maestria'] = per_df['_norm'].apply(lambda k: maestria_val if has_flag(k, maes_set) else 0)
                per_df['Especializacao'] = per_df['_norm'].apply(lambda k: (maestria_val // 2) if has_flag(k, esp_set) else 0)

                # TOTAL = Modificador do Atributo + metade do nível + maestria (+ metade da maestria se especialização)
                per_df['Total'] = per_df['ModAtributo'] + half_level + per_df['Maestria'] + per_df['Especializacao']

                # exibição (duas colunas)
                show_cols = ['Pericia', 'Atributo', 'ModAtributo', 'Total']
                cper1, cper2 = st.columns(2)
                mid = int(math.ceil(len(per_df) / 2))

                with cper1:
                    st.dataframe(per_df.iloc[:mid][show_cols], use_container_width=True, hide_index=True)
                with cper2:
                    st.dataframe(per_df.iloc[mid:][show_cols], use_container_width=True, hide_index=True)


    with col_inv2:                
        with st.container(border=True):
            st.subheader('Spores, invocação de '+str(graus_invocacoes.get('Spores')))
            a1, a2 = st.columns([1,2])
            a1.image(fotos_invocacoes.get('Spores'))
            a2.write('Spores é uma amálgama de fungos infundido com a energia amaldiçoada reversa de Frank, sendo capaz de curar seus aliados ou até mesmo seu próprio controlador.')
            a2.write('Com uma ação complexa, pode curar 2d6+3 em um alcance de 6 metros.')
            a2.write('Com uma ação simples, pode garantir +2 em acerto para um aliado em um alcance de 6 metros.')
            c1, c2 = st.columns(2)
            c1.metric("PV", PV_inv.get('Spores'))
            c1.metric("CA", CA_inv.get('Spores'))
            c2.number_input(label="PV Atual", min_value=0, step=1, key="pv_atual_spores")
            c2.metric('Movimento', movimento_inv.get('Spores'))
            st.markdown('---')
            st.markdown('#### Atributos')
            ai1, ai2 = st.columns(2)

            # Primeira coluna: For, Des, Con
            for _, row in pd.read_csv(atributos_invocacoes.get('Spores')).iloc[0:3].iterrows():
                ai1.write(f"**{row['Atributo']}**: {row['Valor']} ({row['Modificador']:+d})")

            # Segunda coluna: Int, Sab, Car
            for _, row in pd.read_csv(atributos_invocacoes.get('Spores')).iloc[3:6].iterrows():
                ai2.write(f"**{row['Atributo']}**: {row['Valor']} ({row['Modificador']:+d})")
            
            st.markdown('---')
            st.markdown('#### Perícias')

            # --- parâmetros
            half_level = nivel // 2
            maestria_val = math.ceil(1 + nivel / 4)

            # normalizadores
            def norm_attr(x: str) -> str:
                m = {
                    'FOR': 'For',
                    'DES': 'Des', 'DEX': 'Des',
                    'CON': 'Con',
                    'INT': 'Int',
                    'SAB': 'Sab', 'WIS': 'Sab',
                    'CAR': 'Car', 'CHA': 'Car',
                }
                key = str(x).strip().upper()
                return m.get(key, str(x).strip())

            def norm_pericia(x: str) -> str:
                return str(x).strip().casefold()

            # sets de maestria/especialização
            maes_set = {norm_pericia(p) for p in (maestrias_invocacoes.get('Spores') or [])}
            esp_set  = {norm_pericia(p) for p in (especializacao_invocacoes.get('Spores') or [])}

            # mapa de modificadores de atributo
            _df_attr = pd.read_csv(atributos_invocacoes.get('Spores'))
            attr_mod_map = {
                norm_attr(a): int(m)
                for a, m in zip(_df_attr['Atributo'], _df_attr['Modificador'])
            }

            # base de perícias
            per_df = df_per_inv[['Pericia', 'Atributo']].copy()
            per_df['Atributo'] = per_df['Atributo'].apply(norm_attr)

            # modificador do atributo
            per_df['ModAtributo'] = per_df['Atributo'].map(attr_mod_map).fillna(0).astype(int)

            # flags
            def has_flag(pname_norm: str, flag_set: set) -> bool:
                return pname_norm in flag_set or (pname_norm.endswith('s') and pname_norm[:-1] in flag_set)

            per_df['_norm'] = per_df['Pericia'].apply(norm_pericia)
            per_df['Maestria'] = per_df['_norm'].apply(lambda k: maestria_val if has_flag(k, maes_set) else 0)
            per_df['Especializacao'] = per_df['_norm'].apply(lambda k: (maestria_val // 2) if has_flag(k, esp_set) else 0)

            # total
            per_df['Total'] = per_df['ModAtributo'] + half_level + per_df['Maestria'] + per_df['Especializacao']

            # exibição
            show_cols = ['Pericia', 'Atributo', 'ModAtributo', 'Total']
            cper1, cper2 = st.columns(2)
            mid = int(math.ceil(len(per_df) / 2))

            with cper1:
                st.dataframe(per_df.iloc[:mid][show_cols], use_container_width=True, hide_index=True)
            with cper2:
                st.dataframe(per_df.iloc[mid:][show_cols], use_container_width=True, hide_index=True)


    with col_inv3:                
        with st.container(border=True):
            st.subheader('Thornslinger, invocação de '+str(graus_invocacoes.get('Thornslinger')))
            a1, a2 = st.columns([1,2])
            a1.image(fotos_invocacoes.get('Thornslinger'))
            a2.write('Thornslinger é um corpo amaldiçoado moldado pela vegetação hostil para combater à distância.')
            a2.write('Com uma ação complexa, pode lançar uma saraivada de espinhos até 9 metros, causando 2d12 de dano.')
            a2.write('Com uma ação simples, atrapalha os ataques de seus inimigos, causando -4 nas rolagens de ataque até 6 metros.')
            c1, c2 = st.columns(2)
            c1.metric("PV", PV_inv.get('Thornslinger'))
            c1.metric("CA", CA_inv.get('Thornslinger'))
            c2.number_input(label="PV Atual", min_value=0, step=1, key="pv_atual_thornslinger")
            c2.metric('Movimento', movimento_inv.get('Thornslinger'))
            st.markdown('---')
            st.markdown('#### Atributos')
            ai1, ai2 = st.columns(2)

            # Primeira coluna: For, Des, Con
            for _, row in pd.read_csv(atributos_invocacoes.get('Thornslinger')).iloc[0:3].iterrows():
                ai1.write(f"**{row['Atributo']}**: {row['Valor']} ({row['Modificador']:+d})")

            # Segunda coluna: Int, Sab, Car
            for _, row in pd.read_csv(atributos_invocacoes.get('Thornslinger')).iloc[3:6].iterrows():
                ai2.write(f"**{row['Atributo']}**: {row['Valor']} ({row['Modificador']:+d})")
            
            st.markdown('---')
            st.markdown('#### Perícias')

            # --- parâmetros
            half_level = nivel // 2
            maestria_val = math.ceil(1 + nivel / 4)

            # normalizadores
            def norm_attr(x: str) -> str:
                m = {
                    'FOR': 'For',
                    'DES': 'Des', 'DEX': 'Des',
                    'CON': 'Con',
                    'INT': 'Int',
                    'SAB': 'Sab', 'WIS': 'Sab',
                    'CAR': 'Car', 'CHA': 'Car',
                }
                key = str(x).strip().upper()
                return m.get(key, str(x).strip())

            def norm_pericia(x: str) -> str:
                return str(x).strip().casefold()

            # sets de maestria/especialização
            maes_set = {norm_pericia(p) for p in (maestrias_invocacoes.get('Thornslinger') or [])}
            esp_set  = {norm_pericia(p) for p in (especializacao_invocacoes.get('Thornslinger') or [])}

            # mapa de modificadores de atributo
            _df_attr = pd.read_csv(atributos_invocacoes.get('Thornslinger'))
            attr_mod_map = {
                norm_attr(a): int(m)
                for a, m in zip(_df_attr['Atributo'], _df_attr['Modificador'])
            }

            # base de perícias
            per_df = df_per_inv[['Pericia', 'Atributo']].copy()
            per_df['Atributo'] = per_df['Atributo'].apply(norm_attr)

            # modificador do atributo
            per_df['ModAtributo'] = per_df['Atributo'].map(attr_mod_map).fillna(0).astype(int)

            # flags
            def has_flag(pname_norm: str, flag_set: set) -> bool:
                return pname_norm in flag_set or (pname_norm.endswith('s') and pname_norm[:-1] in flag_set)

            per_df['_norm'] = per_df['Pericia'].apply(norm_pericia)
            per_df['Maestria'] = per_df['_norm'].apply(lambda k: maestria_val if has_flag(k, maes_set) else 0)
            per_df['Especializacao'] = per_df['_norm'].apply(lambda k: (maestria_val // 2) if has_flag(k, esp_set) else 0)

            # total
            per_df['Total'] = per_df['ModAtributo'] + half_level + per_df['Maestria'] + per_df['Especializacao']

            # exibição
            show_cols = ['Pericia', 'Atributo', 'ModAtributo', 'Total']
            cper1, cper2 = st.columns(2)
            mid = int(math.ceil(len(per_df) / 2))

            with cper1:
                st.dataframe(per_df.iloc[:mid][show_cols], use_container_width=True, hide_index=True)
            with cper2:
                st.dataframe(per_df.iloc[mid:][show_cols], use_container_width=True, hide_index=True)

    #st.sidebar.subheader('debugging')
    #st.sidebar.image(fotos_invocacoes.get(invocacao_selecionada))
    #st.sidebar.write(invocacao_selecionada)

invocacoes_tab()