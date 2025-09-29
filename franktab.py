import streamlit as st
import math
import random
from datetime import datetime
from html import escape
import pandas as pd
import numpy as np

def frank_tab():

    def rolar_pericia(nome: str, total: int) -> dict:
        """Rola 1d20 + total para teste de perícia."""
        d20 = random.randint(1, 20)
        return {
            "Habilidade": f"Perícia – {nome}",
            "Rolagens": [d20],            # mostra o d20
            "Ataque": d20 + int(total),   # 'show_result' exibe como Ataque/Teste
        }

    def pericias_ui(df):
        st.subheader('Tabela Perícias')

        col_pericia = "Perícia" if "Perícia" in df.columns else "Pericia"

        # divide o df igualmente em 2 blocos
        n = len(df)
        mid = (n + 1) // 2
        bloco_esq = df.iloc[:mid].reset_index(drop=True)
        bloco_dir = df.iloc[mid:].reset_index(drop=True)

        col_esq, col_dir = st.columns(2, gap="large")

        def render_bloco(container, bloco_df, bloco_tag):
            with container:
                # Cabeçalho visual
                h1, h2, h3 = st.columns([3, 2, 1])
                h1.markdown("**Perícia**")
                h2.markdown("**Atributo**")
                h3.markdown("**Total**")

                # Linhas com botão no Total
                for i, row in bloco_df[[col_pericia, "Atributo", "Total"]].iterrows():
                    c1, c2, c3 = st.columns([3, 2, 1])
                    c1.write(row[col_pericia])
                    c2.write(row["Atributo"])
                    key = f"roll_skill_{bloco_tag}_{i}_{row[col_pericia]}"
                    if c3.button(str(row["Total"]), key=key, use_container_width=True):
                        st.session_state["skill_last_output"] = (
                            f"Perícia: {row[col_pericia]}",
                            rolar_pericia(row[col_pericia], int(row["Total"]))
                        )

        render_bloco(col_esq, bloco_esq, "L")
        render_bloco(col_dir, bloco_dir, "R")

    # ---------------------------
    # Utilitários
    # ---------------------------
    def dado(faces: int, vezes: int = 1) -> list[int]:
        """Rola 'vezes' dados de 'faces' e retorna a lista com os resultados."""
        return [random.randint(1, faces) for _ in range(vezes)]

    def dado_cura_aprimorada(faces: int, vezes: int = 1) -> list[int]:
        return [random.randint(3, faces) for _ in range(vezes)]

    def mod(atr: int) -> int:
        """Modificador de atributo: floor((atributo-10)/2)."""
        return (atr - 10) // 2

    def add_log(msg: str, payload: dict):
        """Salva o resultado no histórico da sessão."""
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.insert(0, {"msg": msg, "payload": payload, "ts": datetime.now().strftime("%H:%M:%S")})

    def _pills(items):
        if not items: return ""
        html = "".join(f'<span class="pill">{escape(str(i))}</span>' for i in items)
        return f"<div>{html}</div>"

    def _dice_pills(rolls):
        if not rolls: return ""
        html = "".join(f'<span class="die">{escape(str(r))}</span>' for r in rolls)
        return f"<div>{html}</div>"

    def _find_numeric_by_keywords(data: dict, keywords: tuple[str, ...]):
        """Procura um valor numérico por palavra-chave no nome da chave."""
        for k, v in data.items():
            if isinstance(v, (int, float)):
                kl = k.lower()
                for kw in keywords:
                    if kw in kl:
                        return k, v  # retorna a chave original e o valor
        return None, None

    def show_result(title: str, data: dict):
        """Render amigável: decide o 'Resultado' de forma robusta."""
        # 1) tenta pegar "dano"/"cura" em qualquer variação do nome
        key, val = _find_numeric_by_keywords(data, ("dano", "cura"))

        if key is not None:
            primary_label = "Dano" if "dano" in key.lower() else "Cura"
            primary_value = val
        else:
            # 2) fallback: soma rolagens + mods/bônus numéricos, se existirem
            rolls = data.get("Rolagens") or data.get("rolagens") or []
            total = sum(r for r in rolls if isinstance(r, (int, float)))

            # procura campos numéricos que sejam modificadores/bônus
            bonus = 0
            for k, v in data.items():
                if isinstance(v, (int, float)):
                    kl = k.lower()
                    if "mod" in kl or "bônus" in kl or "bonus" in kl:
                        bonus += v

            if rolls:
                primary_label = "Resultado"
                primary_value = total + bonus
            else:
                # 3) último recurso: mostra ataque/CD ou "-"
                primary_label = "Resultado"
                primary_value = (
                    data.get("Rolagem Acerto")
                    or data.get("Ataque")
                    or data.get("Acerto")
                    or data.get("CD do TR")
                    or data.get("CD")
                    or "-"
                )

        alcance = data.get("Alcance") or data.get("alcance")
        efeito  = data.get("Efeito") or data.get("efeito")
        rolls   = data.get("Rolagens") or data.get("rolagens") or []

        with st.container(border=True):
            st.markdown(f"### {title}")

            left, right = st.columns([2, 1])

            with left:
                st.markdown(f'<div class="sec-label">{escape(primary_label)}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="big-num">{escape(str(primary_value))}</div>', unsafe_allow_html=True)

                if rolls:
                    st.caption("Rolagens")
                    st.markdown(_dice_pills(rolls), unsafe_allow_html=True)

                chips = []
                if alcance: chips.append(f"Alcance: {alcance}")
                if efeito:  chips.append(f"Efeito: {efeito}")
                if chips:
                    st.markdown(_pills(chips), unsafe_allow_html=True)

            with right:
                atk_total = data.get("Rolagem Acerto") or data.get("Ataque") or data.get("Acerto")
                cd_tr     = data.get("CD do TR") or data.get("CD")
                if atk_total is not None:
                    st.metric("Total", atk_total)
                if cd_tr is not None:
                    st.metric("CD do TR", cd_tr)

        add_log(title, data)

    # ---------------------------
    # FICHA (base do usuário)
    # ---------------------------
    nivel = 6

    # Atributos
    For = 10
    Des = 16
    Con = 14
    Int = 10
    Sab = 22
    Car = 11

    # Derivados
    PV = 65
    PE = 5 * nivel + mod(Sab)          # Pontos de energia
    maestria = math.ceil(1 + nivel/4)  # Maestria
    CA_Natural, Uniforme, Escudo, Outros = 10, 2, 0, 3
    CA = CA_Natural + Uniforme + Escudo + Outros + mod(Des)

    # ---------------------------
    # Habilidades (coringas)
    # ---------------------------
    def cast_drain():
        return {
            "Habilidade": "Drain",
            "Alcance": "9m",
            "Rolagem Acerto": dado(20)[0] + (1 + nivel // 2),
            "Dano (1d10 + Sab)": sum(dado(10, 1)) + mod(Sab),
        }

    def cast_supply():
        rols = dado_cura_aprimorada(6, 3)
        return {
            "Habilidade": "Supply",
            "Alcance": "9m",
            "Rolagens": rols,
            "Cura (3d6 + Sab)": sum(rols) + mod(Sab),
        }

    def cast_flower_burst():
        rols = dado_cura_aprimorada(6, 2)
        return {
            "Habilidade": "Flower Burst",
            "Alcance": "Raio 6m",
            "Rolagens": rols,
            "Cura (2d6 + Sab)": sum(rols) + mod(Sab),
        }

    def cast_fly_trap():
        rols = dado(10, 1)
        return {
            "Habilidade": "Fly Trap",
            "Alcance": "Raio 6m",
            "CD do TR": 10 + maestria + mod(Sab),
            "Efeito": "Imobilizado",
            "Rolagens": rols,
            "Dano (1d10)": sum(rols),
        }

    def cast_thornshot():
        rols = dado(8, 7)
        return {
            "Habilidade": "Thornshot",
            "Alcance": "9m",
            "CD do TR": 10 + maestria + mod(Sab),
            "Rolagens": rols,
            "Dano (7d8)": sum(rols),
        }

    # Perícias - ETL

    df = pd.read_csv('pericias.csv')

    # Perícias com Maestria
    per_com_maestria = ['Luta', 'Pontaria', 'Prestidigitação', 'Medicina', 'Ocultismo', 'Vontade', 'Astúcia', 'Intimidação']
    per_com_outros = ['Feitiçaria']
    per_outros = 1

    # 1) mapa tolerante de rótulos de atributo -> modificador
    attr_mod_map = {
        "for": mod(For), "força": mod(For), "forca": mod(For), "str": mod(For),
        "des": mod(Des), "dex": mod(Des), "destreza": mod(Des),
        "con": mod(Con), "constituição": mod(Con), "constituicao": mod(Con),
        "int": mod(Int), "inteligência": mod(Int), "inteligencia": mod(Int),
        "sab": mod(Sab), "sabedoria": mod(Sab),
        "car": mod(Car), "carisma": mod(Car),
    }

    # 2) normaliza nomes de colunas (com ou sem acento)
    col_pericia = "Pericia" if "Pericia" in df.columns else "Pericia"

    # 3) componentes
    df["ModAtrib"] = df["Atributo"].map(lambda s: attr_mod_map.get(str(s).strip().lower(), 0))
    df["LvlHalf"]  = nivel // 2
    df["Maestria"] = np.where(df[col_pericia].isin(per_com_maestria), maestria, 0)
    df["Outros"]   = np.where(df[col_pericia].isin(per_com_outros), per_outros, 0)

    # 4) total final
    df["Total"] = df["ModAtrib"] + df["LvlHalf"] + df["Maestria"] + df["Outros"]

    # ---------------------------
    # LAYOUT
    # ---------------------------

    # ----- Colunas principais
    col_ficha, col_pericias, col_habs = st.columns([2, 3, 2], gap="large")

    # ----- Col Pericias
    with col_pericias:
        pericias_ui(df)
    # ----- Col Freakster

    # ----- Coluna Ficha (sidebar visual)
    with col_ficha:
        st.subheader("📜 Ficha do Personagem")
        with st.container(border=True):
            st.markdown("#### Nível e Recursos")
            c1, c2, c3 = st.columns(3)
            c1.metric("Nível", nivel)
            c2.metric(f"Maestria", maestria)
            c3.metric("Atenção", 10+((nivel//2)+mod(Sab)))
            c1.metric("PV", PV)
            c2.metric("PE", PE)
            c3.metric("CA", CA)

            # estado inicial (iguais ao máximo)
            if "pv_atual" not in st.session_state:
                st.session_state.pv_atual = PV
            if "pe_atual" not in st.session_state:
                st.session_state.pe_atual = PE

            # uma única linha com inputs, alinhados com PV/PE
            c1.number_input("PV atual", min_value=0, step=1, key="pv_atual")
            c2.number_input("PE atual", min_value=0, step=1, key="pe_atual")


            st.markdown("---")
            st.markdown("#### Atributos")
            a1, a2 = st.columns(2)
            a1.write(f"**For**: {For} ({mod(For):+d})")
            a1.write(f"**Des**: {Des} ({mod(Des):+d})")
            a1.write(f"**Con**: {Con} ({mod(Con):+d})")
            a2.write(f"**Int**: {Int} ({mod(Int):+d})")
            a2.write(f"**Sab**: {Sab} ({mod(Sab):+d})")
            a2.write(f"**Car**: {Car} ({mod(Car):+d})")
        st.markdown("### 🧾 Histórico")
        
        if "history" in st.session_state and st.session_state.history:
            for item in st.session_state.history[:10]:
                with st.expander(f"[{item['ts']}] {item['msg']}", expanded=False):
                    st.json(item["payload"], expanded=False)
        else:
            st.caption("Sem rolagens ainda. Lance uma habilidade!")

    # ----- Coluna Habilidades
    with col_habs:
        st.subheader("Habilidades")

        # --- botões (apenas definem o 'clicked')
        c1, c2, c3 = st.columns(3)
        c4, c5 = st.columns(2)

        clicked = None
        if c1.button("🩸 Drain", use_container_width=True):
            clicked = ("Drain", cast_drain())
        if c2.button("🌿 Supply", use_container_width=True):
            clicked = ("Supply", cast_supply())
        if c3.button("🌸 Flower Burst", use_container_width=True):
            clicked = ("Flower Burst", cast_flower_burst())
        if c4.button("🪤 Fly Trap", use_container_width=True):
            clicked = ("Fly Trap", cast_fly_trap())
        if c5.button("🌵 Thornshot", use_container_width=True):
            clicked = ("Thornshot", cast_thornshot())

        # salva o último output clicado
        if clicked:
            st.session_state["last_output"] = clicked

        st.markdown("---")

        # --- render fixo do output (sempre abaixo do '---')
        if "last_output" in st.session_state:
            title, payload = st.session_state["last_output"]
            show_result(title, payload)
        else:
            st.caption("Clique numa habilidade para rolar.")

        st.markdown("---")

        st.subheader("Perícias")
        # Resultado fixo acima da tabela
        if "skill_last_output" in st.session_state:
            title, payload = st.session_state["skill_last_output"]
            show_result(title, payload)
        else:
            st.caption("Clique no valor Total para rolar a perícia.")