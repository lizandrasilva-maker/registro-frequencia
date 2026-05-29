import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
from io import BytesIO

st.set_page_config(page_title="Gerador de Registro de Frequência", layout="wide")

st.title("Sistema de Registro de Frequência Manual")
st.subheader("Preencha seus dados e horários para exportar o PDF")

# 1. Informações de Cabeçalho
col1, col2, col3 = st.columns(3)
with col1:
    empresa = st.text_input("Empresa", value="SENAI-WDS")
    lotacao = st.text_input("Lotação", value="")
with col2:
    cnpj = st.text_input("CNPJ", value="")
    mes_ano = st.text_input("Mês/Ano", value="")
with col3:
    matricula = st.text_input("Matrícula", value="")
    funcionario = st.text_input("Nome do Funcionário", value="")

horario = st.text_input("Horário", value="")

if 'rows_data' not in st.session_state:
    st.session_state.rows_data = [

    ]

with st.form("add_row_form"):
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 2, 2, 2, 2, 2, 2])
    with c1: f_dia = st.text_input("Dia")
    with c2: f_p1_e = st.text_input("1º Per Ent.")
    with c3: f_p1_s = st.text_input("1º Per Saí.")
    with c4: f_int_e = st.text_input("Int. Ent.")
    with c5: f_int_s = st.text_input("Int. Saí.")
    with c6: f_p2_e = st.text_input("2º Per Ent.")
    with c7: f_p2_s = st.text_input("2º Per Saí.")
    
    submit = st.form_submit_button("➕ Adicionar Linha à Tabela")
    if submit and f_dia:
        st.session_state.rows_data.append({
            "dia": f_dia, "p1_ent": f_p1_e, "p1_sai": f_p1_s,
            "int_ent": f_int_e, "int_sai": f_int_s,
            "p2_ent": f_p2_e, "p2_sai": f_p2_s
        })

if st.session_state.rows_data:
    try:
        st.session_state.rows_data = sorted(st.session_state.rows_data, key=lambda x: int(x['dia']) if x['dia'].isdigit() else 99)
    except:
        pass
        
    df = pd.DataFrame(st.session_state.rows_data)
    st.dataframe(df, use_container_width=True)
    if st.button("🗑️ Limpar Todos os Registros"):
        st.session_state.rows_data = []
        st.rerun()

class PontoPDF(FPDF):
    def draw_grid(self, emp, cnpj, lot, mes, mat, func, hor, data_rows):
        self.add_page()
        self.set_auto_page_break(False)
        self.set_text_color(0, 0, 0)
        self.set_margins(10, 8, 10)
        
        # Margem total de 190mm de largura útil (X vai de 10 até 200 de forma estrita)
        self.set_line_width(0.3)
        
        # 1. QUADRO SUPERIOR DO LOGOTIPO
        self.rect(10, 8, 190, 22) 
        self.line(56, 8, 56, 30)   
        self.line(146, 8, 146, 30) 
        
        try:
            url = "https://ik.imagekit.io/zrcquvrghb/scala/images.png"
            res = requests.get(url, timeout=5)
            img_bytes = BytesIO(res.content)
            # Altura travada em h=15 para a logo não vazar para o quadro de baixo
            self.image(img_bytes, x=13, y=11, w=38, h=15)
        except:
            self.set_font("Arial", "B", 10)
            self.text(15, 20, "SISTEMA FIEC")
            
        self.set_font("Arial", "B", 12)
        self.set_xy(56, 15)
        self.cell(90, 8, "Registro de Frequência Manual", align="C")
        
        self.set_font("Arial", "", 7.5)
        self.set_xy(148, 11)
        self.cell(40, 3.5, "Código: F2I7-PC12", ln=True)
        self.set_x(148)
        self.cell(40, 3.5, "Versão: 02", ln=True)
        self.set_x(148)
        self.cell(40, 3.5, "Data: 27/01/2026")
        
        # 2. BLOCO DE INFORMAÇÕES DO COLABORADOR (Corrigido o limite direito de 200 para 190mm de largura)
        self.rect(10, 34, 190, 32)
        self.line(130, 34, 130, 48) # Divisória Empresa / CNPJ
        self.line(10, 41, 200, 41)  # Linha horizontal 1
        self.line(10, 48, 200, 48)  # Linha horizontal 2
        self.line(10, 55, 200, 55)  # Linha horizontal 3
        self.line(48, 48, 48, 55)   # Linha vertical Matrícula / Nome
        
        # Rótulos (Labels)
        self.set_font("Arial", "B", 7.5)
        self.text(12, 37.5, "Empresa:")
        self.text(132, 37.5, "CNPJ:")
        self.text(12, 44.5, "Lotação:")
        self.text(132, 44.5, "Mês/Ano:")
        self.text(12, 51.5, "Matrícula:")
        self.text(50, 51.5, "Nome do Funcionário:")
        self.text(12, 58.5, "Horário:")
        
        # Valores
        self.set_font("Arial", "", 9)
        self.text(12, 40.5, emp)
        self.text(132, 40.5, cnpj)
        self.text(12, 47.5, lot)
        self.text(132, 47.5, mes)
        self.text(12, 54.5, mat)
        self.text(50, 54.5, func)
        self.text(12, 61.5, hor)
        
        # 3. TABELA DE DIAS (10 + 36 + 36 + 36 + 52 + 20 = 190mm perfeitos)
        start_y = 70
        self.set_xy(10, start_y)
        self.set_font("Arial", "B", 8)
        
        self.cell(10, 10, "Dia", border=1, align="C")
        self.cell(36, 5, "1° período", border=1, align="C")
        self.cell(36, 5, "Intervalo", border=1, align="C")
        self.cell(36, 5, "2° período", border=1, align="C")
        self.cell(52, 5, "Ocorrências", border=1, align="C")
        self.cell(20, 10, "Rubrica", border=1, align="C")
        
        self.set_xy(20, start_y + 5)
        self.set_font("Arial", "B", 7)
        for _ in range(3):
            self.cell(18, 5, "Entrada", border=1, align="C")
            self.cell(18, 5, "Saída", border=1, align="C")
        self.cell(26, 5, "Entrada", border=1, align="C")
        self.cell(26, 5, "Saída", border=1, align="C")
            
        current_y = start_y + 10
        row_height = 5.15 
        
        for i in range(1, 32):
            self.set_xy(10, current_y)
            row_data = next((r for r in data_rows if str(r['dia']) == str(i)), None)
            
            self.set_font("Arial", "B", 7.5)
            self.cell(10, row_height, str(i), border=1, align="C")
            
            self.set_font("Arial", "", 7.5)
            if row_data:
                self.cell(18, row_height, row_data['p1_ent'] if row_data['p1_ent'] else "", border=1, align="C")
                self.cell(18, row_height, row_data['p1_sai'] if row_data['p1_sai'] else "", border=1, align="C")
                self.cell(18, row_height, row_data['int_ent'] if row_data['int_ent'] else "", border=1, align="C")
                self.cell(18, row_height, row_data['int_sai'] if row_data['int_sai'] else "", border=1, align="C")
                self.cell(18, row_height, row_data['p2_ent'] if row_data['p2_ent'] else "", border=1, align="C")
                self.cell(18, row_height, row_data['p2_sai'] if row_data['p2_sai'] else "", border=1, align="C")
            else:
                for _ in range(6):
                    self.cell(18, row_height, "", border=1, align="C")
            
            self.cell(26, row_height, "", border=1, align="C")
            self.cell(26, row_height, "", border=1, align="C")
            self.cell(20, row_height, "", border=1, align="C")
            
            current_y += row_height
            
        # Totais
        self.set_xy(10, current_y + 1)
        self.set_font("Arial", "B", 8)
        self.cell(108, 5, "", border=0)
        self.cell(10, 5, "Totais", border=0, align="R")
        self.cell(26, 5, "", border=1)
        self.cell(26, 5, "", border=1)
        
        # 4. ASSINATURAS NO RODAPÉ
        sig_y = current_y + 14
        self.line(15, sig_y, 95, sig_y)
        self.line(115, sig_y, 195, sig_y)
        
        self.set_font("Arial", "", 8)
        self.set_xy(15, sig_y + 1)
        self.cell(80, 4, "Assinatura Gestor Imediato e carimbo", border=0, align="C")
        self.set_xy(115, sig_y + 1)
        self.cell(80, 4, "Nome completo do funcionário", border=0, align="C")

# --- EXECUÇÃO DO STREAMLIT ---
st.markdown("---")
st.markdown("### 📥 Exportar Documento")

try:
    pdf = PontoPDF()
    pdf.draw_grid(empresa, cnpj, lotacao, mes_ano, matricula, funcionario, horario, st.session_state.rows_data)
    pdf_output = bytes(pdf.output())

    st.download_button(
        label="⬇️ Baixar Registro de Frequência PDF",
        data=pdf_output,
        file_name=f"Registro_Frequencia_{mes_ano.replace('/','_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
except Exception as e:
    st.error(f"Erro ao gerar o PDF. Verifique as coordenadas: {e}")
