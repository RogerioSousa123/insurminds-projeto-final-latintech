from __future__ import annotations

import base64
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

LOGO_DATA_URI = "data:image/png;base64," + base64.b64encode(
    (PROJECT_ROOT / "assets" / "logo-latin-re.png").read_bytes()
).decode("ascii")

import pandas as pd
import plotly.express as px
import streamlit as st

from insurminds.config import Settings
from insurminds.domain.models import AttentionLevel, FieldStatus, PolicyAnalysis
from insurminds.llm.providers import LLMConfigurationError, build_provider
from insurminds.services.chat_service import ChatService
from insurminds.services.comparison_service import ComparisonService
from insurminds.services.document_processor import DocumentProcessingError
from insurminds.services.orchestrator import AnalysisOrchestrator
from insurminds.services.report_service import build_comparison_pdf
from insurminds.storage.repository import AnalysisRepository


st.set_page_config(
    page_title="InsurMinds D&O Intelligence",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --im-primary: #18C2F2;
        --im-primary-dark: #078CB8;
        --im-navy: #102A43;
        --im-text: #243B53;
        --im-muted: #627D98;
        --im-bg: #F5FAFD;
        --im-surface: #FFFFFF;
        --im-border: #DCECF3;
        --im-soft: #EAF9FE;
    }

    .stApp {
        background:
            radial-gradient(circle at 92% 2%, rgba(24, 194, 242, .13), transparent 24rem),
            linear-gradient(180deg, #FFFFFF 0%, var(--im-bg) 34%, #F8FBFD 100%);
        color: var(--im-text);
    }
    [data-testid="stHeader"] {background: transparent;}
    [data-testid="stToolbar"], #MainMenu, footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    .block-container {
        max-width: 1320px;
        padding-top: 1.35rem;
        padding-bottom: 3.5rem;
    }

    .im-hero {
        position: relative;
        overflow: hidden;
        padding: 2.3rem 2.6rem 2.15rem;
        margin-bottom: 1.15rem;
        border: 1px solid rgba(24, 194, 242, .24);
        border-radius: 1.4rem;
        background: linear-gradient(118deg, #FFFFFF 0%, #F4FCFF 68%, #E5F9FF 100%);
        box-shadow: 0 18px 55px rgba(16, 42, 67, .075);
    }
    .im-hero::after {
        content: "";
        position: absolute;
        width: 18rem;
        height: 18rem;
        right: -7rem;
        top: -10rem;
        border-radius: 50%;
        background: rgba(24, 194, 242, .18);
    }
    .im-brand {
        display: flex;
        align-items: center;
        gap: .9rem;
        margin-bottom: 1.35rem;
    }
    .im-logo {
        width: 6.4rem;
        height: auto;
        display: block;
        object-fit: contain;
    }
    .im-brand-separator {
        width: 1px;
        height: 2.7rem;
        background: #CFE7F0;
    }
    .im-product-name {
        display: flex;
        flex-direction: column;
        gap: .14rem;
        color: var(--im-navy);
        line-height: 1;
    }
    .im-product-name strong {
        font-size: .92rem;
        font-weight: 800;
        letter-spacing: -.01em;
    }
    .im-product-name small {
        color: var(--im-primary-dark);
        font-size: .63rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .im-hero h1 {
        max-width: 760px;
        margin: 0;
        color: var(--im-navy);
        font-size: clamp(2rem, 3.8vw, 3.35rem);
        line-height: 1.04;
        letter-spacing: -.045em;
        font-weight: 760;
    }
    .im-hero p {
        max-width: 720px;
        margin: 1rem 0 1.25rem;
        color: var(--im-muted);
        font-size: 1.05rem;
        line-height: 1.65;
    }
    .im-chips {display: flex; flex-wrap: wrap; gap: .55rem;}
    .im-chip {
        padding: .42rem .72rem;
        border: 1px solid var(--im-border);
        border-radius: 999px;
        background: rgba(255,255,255,.82);
        color: #36566F;
        font-size: .78rem;
        font-weight: 650;
    }

    .im-flow {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: .8rem;
        margin: 0 0 1.35rem;
    }
    .im-flow-card {
        padding: 1rem 1.1rem;
        border: 1px solid var(--im-border);
        border-radius: .9rem;
        background: rgba(255,255,255,.86);
        box-shadow: 0 8px 24px rgba(16,42,67,.04);
    }
    .im-flow-number {
        color: var(--im-primary-dark);
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    .im-flow-title {margin-top: .2rem; color: var(--im-navy); font-size: .94rem; font-weight: 720;}
    .im-flow-copy {margin-top: .16rem; color: var(--im-muted); font-size: .78rem; line-height: 1.4;}

    div[data-baseweb="tab-list"], div[role="tablist"] {
        gap: .35rem;
        padding: .35rem;
        border: 1px solid var(--im-border);
        border-radius: .85rem;
        background: rgba(255,255,255,.9);
        box-shadow: 0 8px 24px rgba(16,42,67,.035);
    }
    button[data-baseweb="tab"], button[role="tab"], div[role="tab"] {
        height: 2.6rem;
        padding: 0 1.05rem;
        border-radius: .62rem;
        color: var(--im-muted);
        font-weight: 650;
        cursor: pointer;
    }
    button[data-baseweb="tab"][aria-selected="true"], button[role="tab"][aria-selected="true"],
    div[role="tab"][aria-selected="true"] {
        background: var(--im-soft);
        color: #057EA8;
    }
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"],
    .react-aria-SelectionIndicator {display: none !important;}

    h1, h2, h3, h4 {color: var(--im-navy); letter-spacing: -.025em;}
    h2 {font-size: 1.55rem !important; margin-top: .4rem !important;}
    p, label, [data-testid="stCaptionContainer"] {color: var(--im-muted);}

    [data-testid="stMetric"] {
        padding: 1rem 1.05rem;
        border: 1px solid var(--im-border);
        border-radius: .9rem;
        background: rgba(255,255,255,.92);
        box-shadow: 0 9px 28px rgba(16,42,67,.045);
    }
    [data-testid="stMetricLabel"] {color: var(--im-muted);}
    [data-testid="stMetricValue"] {color: var(--im-navy); font-weight: 750;}

    [data-testid="stFileUploaderDropzone"] {
        min-height: 11rem;
        border: 1.5px dashed #9BDFF3;
        border-radius: 1rem;
        background: linear-gradient(135deg, #FFFFFF 0%, #F0FBFF 100%);
    }
    [data-testid="stFileUploaderDropzone"]:hover {border-color: var(--im-primary);}

    .stButton > button, .stDownloadButton > button {
        min-height: 2.65rem;
        border-radius: .7rem;
        border-color: var(--im-border);
        font-weight: 680;
        transition: all .18s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: var(--im-primary);
        color: #057EA8;
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(24,194,242,.13);
    }
    .stButton > button[kind="primary"], button[kind="primary"] {
        border: 1px solid var(--im-primary);
        background: var(--im-primary);
        color: #073B4C;
        box-shadow: 0 8px 20px rgba(24,194,242,.22);
    }
    .stButton > button[kind="primary"]:hover, button[kind="primary"]:hover {
        border-color: #08AFDC;
        background: #08B8E8;
        color: #052F3D;
    }

    [data-testid="stDataFrame"], [data-testid="stPlotlyChart"], details {
        overflow: hidden;
        border: 1px solid var(--im-border);
        border-radius: .9rem;
        background: white;
        box-shadow: 0 8px 25px rgba(16,42,67,.035);
    }
    [data-testid="stAlert"] {border-radius: .8rem;}
    [data-testid="stStatusWidget"] {border-color: var(--im-border); border-radius: .85rem;}
    div[data-baseweb="select"] > div, textarea, input {
        border-color: var(--im-border) !important;
        border-radius: .7rem !important;
    }
    hr {border-color: var(--im-border);}

    .im-footer {
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--im-border);
        color: #829AB1;
        font-size: .75rem;
        text-align: center;
    }

    @media (max-width: 800px) {
        .block-container {padding: .8rem .85rem 2.5rem;}
        .im-hero {padding: 1.5rem 1.25rem; border-radius: 1rem;}
        .im-flow {grid-template-columns: 1fr;}
        button[data-baseweb="tab"] {padding: 0 .65rem; font-size: .82rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def resources():
    settings = Settings()
    repository = AnalysisRepository(settings.database_path)
    provider = build_provider(settings)
    orchestrator = AnalysisOrchestrator(settings, provider, repository)
    return settings, repository, provider, orchestrator


try:
    settings, repository, provider, orchestrator = resources()
    resource_error = None
except (LLMConfigurationError, ValueError) as exc:
    settings = Settings()
    repository = AnalysisRepository(settings.database_path)
    provider = None
    orchestrator = None
    resource_error = str(exc)


if "comparison" not in st.session_state:
    st.session_state.comparison = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


def analysis_label(analysis: PolicyAnalysis) -> str:
    return f"{analysis.document.filename} · {analysis.created_at[:16].replace('T', ' ')} · {analysis.id[:8]}"


def status_text(status: FieldStatus) -> str:
    return {
        FieldStatus.ENCONTRADO: "Encontrado",
        FieldStatus.NAO_LOCALIZADO: "Não localizado",
        FieldStatus.AMBIGUO: "Ambíguo",
        FieldStatus.NAO_APLICAVEL: "Não aplicável",
    }[status]


def attention_icon(level: AttentionLevel) -> str:
    return {
        AttentionLevel.BAIXA: "🟢 Baixa",
        AttentionLevel.MEDIA: "🟡 Média",
        AttentionLevel.ALTA: "🔴 Alta",
        AttentionLevel.INDETERMINADA: "⚪ Indeterminada",
    }[level]


st.markdown(
    f"""
    <section class="im-hero">
        <div class="im-brand">
            <img class="im-logo" src="{LOGO_DATA_URI}" alt="Latin Re">
            <span class="im-brand-separator"></span>
            <span class="im-product-name"><strong>InsurMinds</strong><small>D&amp;O Intelligence</small></span>
        </div>
        <h1>Apólices complexas.<br>Comparações mais claras.</h1>
        <p>Organize cláusulas, encontre diferenças relevantes e confira cada conclusão diretamente na página de origem.</p>
        <div class="im-chips">
            <span class="im-chip">PDF e imagens</span>
            <span class="im-chip">26 critérios D&amp;O</span>
            <span class="im-chip">Evidências por página</span>
            <span class="im-chip">Relatório comparativo</span>
        </div>
    </section>
    <section class="im-flow">
        <div class="im-flow-card"><div class="im-flow-number">Etapa 01</div><div class="im-flow-title">Envie as apólices</div><div class="im-flow-copy">Adicione dois ou mais documentos para iniciar.</div></div>
        <div class="im-flow-card"><div class="im-flow-number">Etapa 02</div><div class="im-flow-title">Revise as evidências</div><div class="im-flow-copy">Confira valores, cláusulas, páginas e alertas.</div></div>
        <div class="im-flow-card"><div class="im-flow-number">Etapa 03</div><div class="im-flow-title">Compare e exporte</div><div class="im-flow-copy">Visualize diferenças e gere o relatório final.</div></div>
    </section>
    """,
    unsafe_allow_html=True,
)

tab_upload, tab_policies, tab_compare, tab_chat, tab_architecture = st.tabs(
    ["Documentos", "Apólices", "Comparação", "Copiloto", "Como funciona"]
)


with tab_upload:
    st.subheader("Comece pelos documentos")
    st.caption("Envie PDF, PNG, JPG, TIFF ou WebP · até 50 MB por arquivo")
    if resource_error:
        st.error("Não foi possível inicializar a IA. Confira as variáveis do arquivo .env e reinicie a aplicação.")
    elif settings.llm_provider == "demo":
        st.info("A aplicação está no modo de demonstração. Configure uma API de IA antes da apresentação final.")
    uploads = st.file_uploader(
        "Selecione duas ou mais apólices",
        type=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "webp"],
        accept_multiple_files=True,
    )
    force = st.checkbox("Reprocessar mesmo quando existir análise em cache", value=False)
    start = st.button(
        "Processar documentos",
        type="primary",
        disabled=not uploads or orchestrator is None,
        use_container_width=False,
    )
    if start and uploads and orchestrator:
        completed = 0
        for file_index, upload in enumerate(uploads, start=1):
            status = st.status(f"Processando {upload.name}", expanded=True)
            progress_bar = status.progress(0.0)
            message_slot = status.empty()

            def notify(event, *, _slot=message_slot, _bar=progress_bar):
                _slot.write(f"**{event.stage.title()}:** {event.message}")
                _bar.progress(event.progress)

            try:
                analysis, cached = orchestrator.process(
                    filename=upload.name,
                    content=upload.getvalue(),
                    mime_type=upload.type,
                    force=force,
                    notify=notify,
                )
                found = sum(field.status == FieldStatus.ENCONTRADO for field in analysis.fields)
                status.write(f"{found} de {len(analysis.fields)} critérios encontrados.")
                status.update(
                    label=f"{upload.name}: {'recuperado do cache' if cached else 'processado com sucesso'}",
                    state="complete",
                    expanded=False,
                )
                completed += 1
            except (DocumentProcessingError, LLMConfigurationError, ValueError) as exc:
                status.error(str(exc))
                status.update(label=f"Falha em {upload.name}", state="error", expanded=True)
            except Exception as exc:
                status.error(f"Erro inesperado: {exc}")
                status.update(label=f"Falha em {upload.name}", state="error", expanded=True)
        if completed:
            st.success(f"{completed} documento(s) disponível(is) nas abas de análise e comparação.")


analyses = repository.list_analyses()
analysis_by_id = {analysis.id: analysis for analysis in analyses}


with tab_policies:
    st.subheader("Apólices processadas")
    if not analyses:
        st.info("Processe ao menos uma apólice na primeira aba.")
    else:
        selected_id = st.selectbox(
            "Análise",
            options=list(analysis_by_id),
            format_func=lambda item: analysis_label(analysis_by_id[item]),
        )
        selected = analysis_by_id[selected_id]
        found_count = sum(field.status == FieldStatus.ENCONTRADO for field in selected.fields)
        ambiguous_count = sum(field.status == FieldStatus.AMBIGUO for field in selected.fields)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Páginas", selected.document.page_count)
        col2.metric("Critérios encontrados", f"{found_count}/{len(selected.fields)}")
        col3.metric("Ambíguos", ambiguous_count)
        col4.metric("Tempo", f"{selected.elapsed_seconds:.1f}s")

        rows = [
            {
                "Categoria": field.category,
                "Critério": field.label,
                "Status": status_text(field.status),
                "Valor": field.value_text or "—",
                "Confiança": f"{field.confidence:.0%}" if field.confidence else "—",
                "Páginas": ", ".join(str(evidence.page) for evidence in field.evidences) or "—",
            }
            for field in selected.fields
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=560)

        with st.expander("Evidências e auditoria"):
            evidenced = [field for field in selected.fields if field.evidences]
            for field in evidenced:
                st.markdown(f"**{field.label}** — {field.value_text or status_text(field.status)}")
                if field.summary:
                    st.caption(field.summary)
                for evidence in field.evidences:
                    st.markdown(f"> Página {evidence.page} · confiança {evidence.confidence:.0%}: {evidence.excerpt}")
            if not evidenced:
                st.info("Nenhuma evidência disponível.")

        if selected.warnings:
            with st.expander(f"Avisos do processamento ({len(selected.warnings)})"):
                for warning in selected.warnings:
                    st.warning(warning)

        with st.expander("Detalhes técnicos do processamento"):
            detail1, detail2, detail3 = st.columns(3)
            detail1.metric("Páginas com OCR", len(selected.document.ocr_pages))
            detail2.metric("Tokens de entrada", f"{selected.input_tokens:,}")
            detail3.metric("Tokens de saída", f"{selected.output_tokens:,}")
            st.caption(f"Modelo utilizado: {selected.model_name}")

        st.download_button(
            "Baixar análise em JSON",
            data=selected.model_dump_json(indent=2),
            file_name=f"analise_{selected.document.id}.json",
            mime="application/json",
        )


with tab_compare:
    st.subheader("Comparação estruturada")
    if len(analyses) < 2:
        st.info("Processe pelo menos duas apólices para habilitar a comparação.")
    else:
        default_ids = [analysis.id for analysis in analyses[:2]]
        selected_ids = st.multiselect(
            "Apólices",
            options=list(analysis_by_id),
            default=default_ids,
            format_func=lambda item: analysis_label(analysis_by_id[item]),
            max_selections=4,
        )
        ai_summary = st.checkbox("Gerar interpretação executiva com a IA", value=True)
        if st.button("Comparar apólices", type="primary", disabled=len(selected_ids) < 2):
            if provider is None and ai_summary:
                st.error(resource_error or "Provedor de IA indisponível.")
            else:
                if provider is None:
                    from insurminds.llm.providers import DemoProvider

                    comparison_provider = DemoProvider()
                else:
                    comparison_provider = provider
                with st.spinner("Comparando critérios e preparando a análise..."):
                    comparison = ComparisonService(comparison_provider).compare(
                        [analysis_by_id[item] for item in selected_ids], use_ai_summary=ai_summary
                    )
                    repository.save_comparison(comparison)
                    st.session_state.comparison = comparison

        comparison = st.session_state.comparison
        if comparison and all(policy_id in analysis_by_id for policy_id in comparison.policy_ids):
            compared = [analysis_by_id[item] for item in comparison.policy_ids]
            differences = sum(row.is_different for row in comparison.rows)
            high = sum(row.attention == AttentionLevel.ALTA for row in comparison.rows)
            unknown = sum(row.attention == AttentionLevel.INDETERMINADA for row in comparison.rows)
            metric1, metric2, metric3 = st.columns(3)
            metric1.metric("Diferenças", differences)
            metric2.metric("Atenção alta", high)
            metric3.metric("Indeterminadas", unknown)
            st.markdown("#### Resumo executivo")
            st.write(comparison.executive_summary)

            attention_rows = [
                {"Categoria": row.category, "Atenção": attention_icon(row.attention), "Quantidade": 1}
                for row in comparison.rows
            ]
            attention_frame = (
                pd.DataFrame(attention_rows)
                .groupby(["Categoria", "Atenção"], as_index=False)["Quantidade"]
                .sum()
            )
            chart = px.bar(
                attention_frame,
                x="Categoria",
                y="Quantidade",
                color="Atenção",
                title="Mapa de atenção por categoria",
                barmode="stack",
                color_discrete_map={
                    "🟢 Baixa": "#2E9D68",
                    "🟡 Média": "#E5AC3D",
                    "🔴 Alta": "#D95C59",
                    "⚪ Indeterminada": "#A7B2BA",
                },
            )
            chart.update_layout(
                legend_title_text="",
                xaxis_title="",
                yaxis_title="Critérios",
                margin=dict(l=20, r=20, t=55, b=90),
                height=390,
            )
            st.plotly_chart(chart, use_container_width=True)

            matrix_rows = []
            for row in comparison.rows:
                record = {
                    "Categoria": row.category,
                    "Critério": row.label,
                    "Atenção": attention_icon(row.attention),
                }
                for cell in row.cells:
                    column = f"{cell.filename} ({cell.policy_id[:6]})"
                    record[column] = cell.value_text or status_text(cell.status)
                record["Análise"] = row.explanation
                matrix_rows.append(record)
            matrix = pd.DataFrame(matrix_rows)
            st.dataframe(matrix, hide_index=True, use_container_width=True, height=650)

            with st.expander("Conferir evidências da comparação"):
                rows_with_evidence = [row for row in comparison.rows if any(cell.evidences for cell in row.cells)]
                for row in rows_with_evidence:
                    st.markdown(f"**{row.label}** · {attention_icon(row.attention)}")
                    for cell in row.cells:
                        for evidence in cell.evidences:
                            st.markdown(f"> {cell.filename}, p. {evidence.page}: {evidence.excerpt}")

            json_data = comparison.model_dump_json(indent=2)
            csv_data = matrix.to_csv(index=False).encode("utf-8-sig")
            download1, download2, download3 = st.columns(3)
            download1.download_button(
                "Baixar JSON", json_data, "comparacao_insurminds.json", "application/json", use_container_width=True
            )
            download2.download_button(
                "Baixar CSV", csv_data, "comparacao_insurminds.csv", "text/csv", use_container_width=True
            )
            try:
                pdf_data = build_comparison_pdf(comparison, compared)
                download3.download_button(
                    "Baixar relatório PDF",
                    pdf_data,
                    "InsurMinds_Relatorio_Comparativo.pdf",
                    "application/pdf",
                    use_container_width=True,
                )
            except RuntimeError as exc:
                download3.warning(str(exc))

            for caveat in comparison.caveats:
                st.caption("⚠️ " + caveat)


with tab_chat:
    st.subheader("Copiloto com evidências")
    if not analyses:
        st.info("Processe documentos antes de conversar com o copiloto.")
    else:
        chat_default = [item for item in (st.session_state.comparison.policy_ids if st.session_state.comparison else []) if item in analysis_by_id]
        if not chat_default:
            chat_default = [analysis.id for analysis in analyses[:2]]
        chat_ids = st.multiselect(
            "Base da conversa",
            options=list(analysis_by_id),
            default=chat_default,
            format_func=lambda item: analysis_label(analysis_by_id[item]),
            key="chat_policy_ids",
        )
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.form("question_form", clear_on_submit=True):
            question = st.text_area(
                "Pergunta",
                placeholder="Ex.: Qual apólice apresenta maior restrição para custos de defesa?",
                height=85,
            )
            ask = st.form_submit_button("Perguntar", type="primary", disabled=not chat_ids or provider is None)
        if ask and question:
            st.session_state.chat_messages.append({"role": "user", "content": question})
            try:
                with st.spinner("Buscando evidências e elaborando a resposta..."):
                    answer = ChatService(provider).answer(question, [analysis_by_id[item] for item in chat_ids])
            except Exception as exc:
                answer = f"Não foi possível responder: {exc}"
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()
        if st.session_state.chat_messages and st.button("Limpar conversa"):
            st.session_state.chat_messages = []
            st.rerun()


with tab_architecture:
    st.subheader("Como a InsurMinds trabalha")
    st.code(
        """Documento PDF/Imagem
        │
        ▼
Ingestão e validação ──► hash/cache local
        │
        ▼
PyMuPDF + OCR Tesseract ──► texto preservado por página
        │
        ▼
Agente Extrator (API conversacional)
        │
        ▼
Validador de evidências ──► Pydantic ──► SQLite
        │
        ├────────► Comparador determinístico ──► Analista IA ──► PDF/CSV/JSON
        │
        └────────► Recuperação de evidências ──► Copiloto IA
""",
        language="text",
    )
    st.markdown(
        """
        **Princípios implementados**

        - A IA interpreta linguagem; código tradicional compara números, estados e datas.
        - Cada dado aceito precisa de trecho e página verificáveis.
        - A ausência de informação nunca é convertida automaticamente em ausência de cobertura.
        - Chaves ficam somente no ambiente local e não são gravadas no banco.
        - O hash evita chamadas repetidas e o modo demo permite apresentar a interface sem consumo de API.
        - Prompts tratam o documento como dado não confiável para reduzir ataques de injeção.
        """
    )

st.markdown(
    '<div class="im-footer">InsurMinds · Inteligência aplicada à análise de seguros D&amp;O</div>',
    unsafe_allow_html=True,
)
