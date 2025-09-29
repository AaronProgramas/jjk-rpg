import streamlit as st
import math
import random
from datetime import datetime
from html import escape
import pandas as pd
import numpy as np
from franktab import frank_tab
from summons import invocacoes_tab

# ---------------------------
# Configuração da página
# ---------------------------
st.set_page_config(page_title="Ficha Freakster", layout="wide")

st.markdown("""
<style>
.big-num{font-size:2.4rem;font-weight:800;line-height:1;margin:.15rem 0 .35rem 0}
.pill{display:inline-block;padding:.15rem .55rem;border:1px solid rgba(255,255,255,.18);
    border-radius:999px;margin:.15rem .25rem 0 0;background:rgba(255,255,255,.04)}
.die{display:inline-block;font-weight:700;padding:.15rem .45rem;border-radius:.5rem;
    border:1px dashed rgba(255,255,255,.18);margin:.15rem .2rem 0 0}
.sec-label{opacity:.8;font-size:.9rem;margin-top:.25rem}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("Frank Guggenheim")

st.sidebar.image('freak.jpeg')
st.sidebar.subheader('Quem é O Homem?')
st.sidebar.write('Frank Guggenheim, também conhecido como Freak, ou Freakster é um feiticeiro jujutsu focado em dar suporte para a sua equipe, garantindo que nenhum acerto crítico será proferido contra seus companheiros.')
st.sidebar.write('')
st.sidebar.write('Frank é atualmente o considerado o melhor usuário de energia reversa da história, tendo até mesmo reanimado os mortos.')



tab1, tab2 = st.tabs(['Frank Guggenheim', 'Invocações'])

with tab1:
    frank_tab()

with tab2:
    invocacoes_tab()
