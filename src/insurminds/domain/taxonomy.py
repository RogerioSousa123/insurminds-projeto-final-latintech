from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldDefinition:
    key: str
    label: str
    category: str
    description: str
    value_hint: str = "texto"
    attention_if_different: str = "media"


FIELD_DEFINITIONS: tuple[FieldDefinition, ...] = (
    FieldDefinition("seguradora", "Seguradora", "Identificação", "Nome da sociedade seguradora."),
    FieldDefinition("segurado", "Segurado/Tomador", "Identificação", "Pessoa jurídica estipulante ou segurada."),
    FieldDefinition("numero_apolice", "Número da apólice", "Identificação", "Número identificador da apólice."),
    FieldDefinition("vigencia_inicio", "Início de vigência", "Condições gerais", "Data e hora inicial da vigência.", "data ISO AAAA-MM-DD"),
    FieldDefinition("vigencia_fim", "Fim de vigência", "Condições gerais", "Data e hora final da vigência.", "data ISO AAAA-MM-DD"),
    FieldDefinition("limite_maximo_garantia", "Limite máximo de garantia", "Limites e franquias", "Limite agregado ou máximo de responsabilidade da seguradora.", "número e moeda", "alta"),
    FieldDefinition("limites_por_cobertura", "Sublimites por cobertura", "Limites e franquias", "Sublimites aplicáveis a coberturas específicas.", "lista", "alta"),
    FieldDefinition("franquia_geral", "Franquia/participação obrigatória", "Limites e franquias", "Franquia ou participação obrigatória geral.", "número e moeda", "alta"),
    FieldDefinition("cobertura_a", "Cobertura A — administradores", "Coberturas", "Indenização direta aos administradores quando a companhia não os indeniza.", "coberto, não coberto ou condicionado", "alta"),
    FieldDefinition("cobertura_b", "Cobertura B — reembolso à companhia", "Coberturas", "Reembolso à sociedade por indenizações pagas a administradores.", "coberto, não coberto ou condicionado", "alta"),
    FieldDefinition("cobertura_c", "Cobertura C — entidade", "Coberturas", "Cobertura da própria entidade, inclusive reclamações de valores mobiliários quando aplicável.", "coberto, não coberto ou condicionado", "alta"),
    FieldDefinition("custos_defesa", "Custos de defesa", "Coberturas", "Tratamento dos custos de defesa e se consomem o limite.", "texto e booleanos", "alta"),
    FieldDefinition("reclamacoes_trabalhistas", "Reclamações trabalhistas", "Coberturas", "Cobertura relacionada a práticas trabalhistas ou EPL.", "coberto, excluído ou condicionado", "alta"),
    FieldDefinition("investigacoes", "Investigações e processos regulatórios", "Coberturas", "Cobertura para investigações formais, inquéritos ou processos regulatórios.", "coberto, excluído ou condicionado", "alta"),
    FieldDefinition("multas_penalidades", "Multas e penalidades", "Coberturas", "Tratamento de multas, penalidades civis ou administrativas.", "coberto, excluído ou condicionado", "alta"),
    FieldDefinition("responsabilidade_ambiental", "Responsabilidade ambiental", "Coberturas", "Cobertura ou exclusão relacionada a poluição e dano ambiental.", "coberto, excluído ou condicionado", "media"),
    FieldDefinition("atos_dolosos", "Atos dolosos, fraude e vantagem indevida", "Exclusões", "Exclusão por dolo, fraude, ato criminoso ou vantagem pessoal; observar necessidade de decisão final.", "texto", "alta"),
    FieldDefinition("segurado_contra_segurado", "Segurado contra segurado", "Exclusões", "Exclusão de reclamações entre segurados e respectivas exceções.", "texto", "alta"),
    FieldDefinition("fatos_anteriores", "Fatos, processos e circunstâncias anteriores", "Exclusões", "Exclusões de fatos conhecidos, notificações ou processos anteriores.", "texto", "alta"),
    FieldDefinition("data_retroatividade", "Data de retroatividade", "Temporalidade", "Data retroativa ou indicação de retroatividade ilimitada.", "data ou ilimitada", "alta"),
    FieldDefinition("prazo_complementar", "Prazo complementar", "Temporalidade", "Prazo adicional para apresentação de reclamações.", "quantidade de meses", "alta"),
    FieldDefinition("prazo_suplementar", "Prazo suplementar", "Temporalidade", "Prazo suplementar opcional e suas condições.", "quantidade de meses", "media"),
    FieldDefinition("territorio", "Âmbito territorial", "Jurisdição", "Território no qual atos ou reclamações estão cobertos.", "texto", "media"),
    FieldDefinition("jurisdicao", "Âmbito de jurisdição", "Jurisdição", "Tribunais, leis ou jurisdições admitidas e restrições.", "texto", "alta"),
    FieldDefinition("mudanca_controle", "Fusão, aquisição e mudança de controle", "Eventos societários", "Efeitos de mudança de controle, aquisição, fusão ou insolvência.", "texto", "alta"),
    FieldDefinition("cancelamento", "Cancelamento e rescisão", "Condições gerais", "Hipóteses, prazos e efeitos do cancelamento.", "texto", "media"),
)

FIELD_BY_KEY = {item.key: item for item in FIELD_DEFINITIONS}


# Campos que devem representar um único dado da especificação da apólice. Os
# demais campos descrevem cláusulas e podem reunir condições, exclusões e
# extensões complementares sem que isso, por si só, signifique ambiguidade.
SCALAR_FIELD_KEYS = frozenset(
    {
        "seguradora",
        "segurado",
        "numero_apolice",
        "vigencia_inicio",
        "vigencia_fim",
        "limite_maximo_garantia",
        "franquia_geral",
        "data_retroatividade",
    }
)


def taxonomy_for_prompt() -> str:
    return "\n".join(
        f"- {item.key}: {item.label}. {item.description} Formato esperado: {item.value_hint}."
        for item in FIELD_DEFINITIONS
    )
