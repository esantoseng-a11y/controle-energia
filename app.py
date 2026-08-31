import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from datetime import datetime
import io

# Configuração da página
st.set_page_config(
    page_title="Controle de Energia", page_icon="⚡", layout="centered"
)

# Estilo para aumentar fontes e ajustar botões
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-size: 20px !important;
    }
    .stButton>button {
        width: 100%;
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 10px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Preço do kWh e limites das casas
PRECO_KWH = 0.75
LIMITES = {"Dercilio": 400, "Saulo": 500, "Ricardo": 450, "Aligas": 350}

# Inicializa o estado dos dados
if "casas" not in st.session_state:
    st.session_state.casas = {
        "Dercilio": [],
        "Saulo": [],
        "Ricardo": [],
        "Aligas": [],
    }


def gerar_pdf(casas_data):
    """Gera um PDF com os dados de consumo"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo customizado
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12
    )
    
    # Título
    elements.append(Paragraph("⚡ RELATÓRIO DE CONSUMO DE ENERGIA", titulo_style))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Dados de cada casa
    for nome, leituras in casas_data.items():
        total_kwh = 0
        
        # Calcula o consumo total (diferença entre leituras)
        for i in range(1, len(leituras)):
            consumo = leituras[i]['valor'] - leituras[i-1]['valor']
            total_kwh += consumo
        
        custo = total_kwh * PRECO_KWH
        limite = LIMITES[nome]
        
        elements.append(Paragraph(f"Casa: {nome}", heading_style))
        
        # Tabela de dados
        data = [
            ['Métrica', 'Valor'],
            ['Consumo Total', f'{total_kwh:.2f} kWh'],
            ['Custo Total', f'R$ {custo:.2f}'],
            ['Limite Recomendado', f'{limite} kWh'],
            ['Status', 'EXCEDIDO' if total_kwh > limite else 'OK'],
        ]
        
        table = Table(data, colWidths=[2.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Histórico de leituras
        if leituras:
            elementos_hist = ', '.join([f"{x['data']} - {x['valor']:.2f} kWh" for x in leituras])
            elements.append(Paragraph(f"<b>Histórico de Leituras:</b> {elementos_hist}", styles['Normal']))
        else:
            elements.append(Paragraph("<b>Histórico de Leituras:</b> Nenhuma leitura registrada", styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # Resumo total
    elements.append(Paragraph("RESUMO GERAL", heading_style))
    total_geral_kwh = 0
    for leituras in casas_data.values():
        for i in range(1, len(leituras)):
            consumo = leituras[i]['valor'] - leituras[i-1]['valor']
            total_geral_kwh += consumo
    
    custo_geral = total_geral_kwh * PRECO_KWH
    
    resumo_data = [
        ['Descrição', 'Total'],
        ['Consumo Total (Todas as Casas)', f'{total_geral_kwh:.2f} kWh'],
        ['Custo Total (Todas as Casas)', f'R$ {custo_geral:.2f}'],
        ['Preço por kWh', f'R$ {PRECO_KWH:.2f}'],
    ]
    
    resumo_table = Table(resumo_data, colWidths=[2.5*inch, 2.5*inch])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(resumo_table)
    
    # Gera o PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


st.title("⚡ Controle de Consumo de Energia")

# Formulário para adicionar leitura
st.subheader("➕ Adicionar Leitura do Consumo")
casa_selecionada = st.selectbox(
    "Selecione a Casa:", list(st.session_state.casas.keys())
)

col1, col2 = st.columns(2)
with col1:
    data_leitura = st.date_input("Data da Leitura:")
with col2:
    kwh_input = st.number_input(
        "Leitura do Consumo (kWh):", min_value=0.0, step=0.1, format="%.2f"
    )

if st.button("Salvar Leitura"):
    if kwh_input >= 0:
        st.session_state.casas[casa_selecionada].append({
            'data': data_leitura.strftime('%d/%m/%Y'),
            'valor': kwh_input
        })
        st.success(
            f"✅ Leitura de {kwh_input:.2f} kWh adicionada para {casa_selecionada} em {data_leitura.strftime('%d/%m/%Y')}!"
        )
    else:
        st.warning("⚠️ Digite um valor válido.")

st.divider()

# Resumo e cálculos
st.subheader("📊 Resumo das Casas")
relatorio_texto = "=== RELATÓRIO DE CONSUMO DE ENERGIA ===\n\n"

for nome, leituras in st.session_state.casas.items():
    total_kwh = 0
    
    # Calcula o consumo total (diferença entre leituras)
    for i in range(1, len(leituras)):
        consumo = leituras[i]['valor'] - leituras[i-1]['valor']
        total_kwh += consumo
    
    custo = total_kwh * PRECO_KWH
    limite = LIMITES[nome]

    # Prepara texto para exportação
    relatorio_texto += f"Casa: {nome}\n"
    if leituras:
        for i, leitura in enumerate(leituras):
            if i == 0:
                relatorio_texto += f"  [{leitura['data']}] Leitura: {leitura['valor']:.2f} kWh (referência)\n"
            else:
                consumo = leituras[i]['valor'] - leituras[i-1]['valor']
                relatorio_texto += f"  [{leitura['data']}] Leitura: {leitura['valor']:.2f} kWh | Consumo: {consumo:.2f} kWh\n"
    
    relatorio_texto += f"Consumo Total: {total_kwh:.2f} kWh\n"
    relatorio_texto += f"Custo Total: R$ {custo:.2f}\n"
    relatorio_texto += "-" * 40 + "\n"

    # Exibição na tela com cartões
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 🏠 **{nome}**")
            st.write(f"**Consumo Total:** {total_kwh:.2f} kWh")
            st.write(f"**Custo:** R$ {custo:.2f}")
            
            # Exibe histórico de leituras
            if leituras:
                st.write("**Histórico:**")
                for i, leitura in enumerate(leituras):
                    if i == 0:
                        st.write(f"  • {leitura['data']}: {leitura['valor']:.2f} kWh (referência)")
                    else:
                        consumo = leituras[i]['valor'] - leituras[i-1]['valor']
                        st.write(f"  • {leitura['data']}: {leitura['valor']:.2f} kWh (consumo: {consumo:.2f} kWh)")
        
        with col2:
            if total_kwh > limite:
                st.error(
                    f"⚠️ **LIMITE EXCEDIDO!**\n\nMáximo recomendado: {limite} kWh"
                )
            else:
                st.info(f"🟢 Dentro do limite ({limite} kWh)")
        st.divider()

# Botões de ação
st.subheader("⚙️ Ações")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Zerar Todos os Contadores", use_container_width=True):
        st.session_state.casas = {
            "Dercilio": [],
            "Saulo": [],
            "Ricardo": [],
            "Aligas": [],
        }
        st.success("✅ Todos os contadores foram zerados!")
        st.rerun()

with col2:
    casa_limpar = st.selectbox(
        "Selecione a casa para zerar:", 
        list(st.session_state.casas.keys()),
        key="selectbox_limpar"
    )
    if st.button("🗑️ Zerar Esta Casa", use_container_width=True):
        st.session_state.casas[casa_limpar] = []
        st.success(f"✅ Contador de {casa_limpar} foi zerado!")
        st.rerun()

st.divider()

# Botões de exportação
st.subheader("📥 Exportar Dados")
col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="📄 Exportar Relatório (.txt)",
        data=relatorio_texto,
        file_name="controle_energia.txt",
        mime="text/plain",
        use_container_width=True
    )

with col2:
    pdf_buffer = gerar_pdf(st.session_state.casas)
    st.download_button(
        label="📊 Exportar Relatório (.pdf)",
        data=pdf_buffer,
        file_name="controle_energia.pdf",
        mime="application/pdf",
        use_container_width=True
    )
