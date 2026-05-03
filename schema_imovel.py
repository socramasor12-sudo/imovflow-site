"""
schema_imovel.py — Modelo Pydantic para validar JSON V5 de imoveis.

Usado pelo publicar.py para fail-fast antes de qualquer ação irreversivel.
"""
import re
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


PLACEHOLDERS = (
    'ESCREVER AQUI', 'escrever aqui',
    'TODO:', 'PLACEHOLDER', 'XXXX', 'LOREM IPSUM',
)


class Parceiro(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nome:     Optional[str] = ""
    creci:    Optional[str] = ""
    whatsapp: Optional[str] = ""


class Imovel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    titulo:     str = Field(..., min_length=10)
    slug:       str = Field(..., max_length=50)
    tipo:       Literal["casa", "apartamento", "lote", "sobrado", "comercial"]
    finalidade:   Literal["venda", "aluguel"]
    tipo_negocio: Literal["lancamentos", "revendas"] = "revendas"
    valor:      int = Field(..., ge=10_000, le=50_000_000)
    area:       int = Field(..., ge=10, le=100_000)
    quartos:    int = Field(..., ge=0, le=20)
    banheiros:  int = Field(..., ge=0, le=20)
    vagas:      int = Field(..., ge=0, le=20)
    bairro:     str = Field(..., min_length=2)
    cidade:     str = Field(default="Anapolis", min_length=2)
    estado:     str = Field(default="GO", min_length=2, max_length=2)
    descricao:  str

    seo_title:       Optional[str] = Field(default="", max_length=70)
    seo_description: Optional[str] = Field(default="", max_length=160)
    foto_capa:       Optional[str] = ""
    parceiro:        Optional[Parceiro] = None

    # --- validators ---

    @field_validator("slug")
    @classmethod
    def _slug_formato(cls, v):
        if not re.fullmatch(r"[a-z0-9-]+", v):
            raise ValueError(
                f"formato invalido '{v}' - use so letras minusculas, numeros e hifens"
            )
        return v

    @field_validator("finalidade", mode="before")
    @classmethod
    def _finalidade_lower(cls, v):
        return v.lower() if isinstance(v, str) else v

    @field_validator("tipo", mode="before")
    @classmethod
    def _tipo_lower(cls, v):
        return v.lower() if isinstance(v, str) else v

    @field_validator("estado")
    @classmethod
    def _estado_upper(cls, v):
        if not re.fullmatch(r"[A-Z]{2}", v.upper()):
            raise ValueError(f"deve ser sigla de 2 letras (recebido '{v}')")
        return v.upper()

    @field_validator("titulo")
    @classmethod
    def _titulo_nao_eh_slug(cls, v):
        if v.count("-") > 3 and " " not in v:
            raise ValueError(f"parece slug (sem espacos): '{v}'")
        return v

    @field_validator("descricao")
    @classmethod
    def _descricao_valida(cls, v):
        for ph in PLACEHOLDERS:
            if ph in v:
                raise ValueError(f"contem placeholder '{ph}' - preencha antes de publicar")

        texto = re.sub(r"<[^>]+>", "", v).strip()
        if len(texto) < 100:
            raise ValueError(
                f"muito curta ({len(texto)} chars sem HTML, minimo 100)"
            )
        return v


def formatar_erros(exc) -> str:
    """Converte ValidationError do Pydantic em lista legivel para o usuario."""
    linhas = ["ERROS DE VALIDACAO:"]
    for err in exc.errors():
        campo = ".".join(str(p) for p in err["loc"]) if err["loc"] else "(raiz)"
        msg   = err["msg"]
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        linhas.append(f"  - {campo}: {msg}")
    linhas.append("")
    linhas.append("Publicacao abortada. Corrija o JSON e tente novamente.")
    return "\n".join(linhas)


# ============================================================
# NORMALIZACAO V4 (nested, do formulario) -> V5 (flat)
# ============================================================
def normalizar_v4_para_v5(dados: dict, slug_fallback: str = "") -> dict:
    """
    Converte JSON V4 (nested, gerado pelo formulario_corretor.html)
    para V5 (flat, esperado pelo schema Imovel).

    Se o dict ja for V5 flat, retorna sem alteracao.
    """
    # Ja eh V5 flat? (nao tem nó "imovel" na raiz)
    if 'imovel' not in dados:
        return dados

    i   = dados['imovel']
    cla = i.get('classificacao', {})
    inf = i.get('informacoes_basicas', {})
    car = i.get('caracteristicas', {})
    seo = i.get('seo', {})
    fot = i.get('fotos', {})
    pro = i.get('proprietario', {})
    cap = i.get('captacao', {})
    des = i.get('descricao', {})

    # Descricao pode ser string direto OU dict {breve, diferenciais, observacoes}
    if isinstance(des, dict):
        partes = []
        breve = des.get('breve', '').strip()
        if breve:
            partes.append(f"<p>{breve}</p>")
        dif = des.get('diferenciais', [])
        if isinstance(dif, list) and dif:
            itens = "".join(f"<li>{x}</li>" for x in dif if x)
            partes.append(f"<ul>{itens}</ul>")
        obs = des.get('observacoes', '').strip()
        if obs:
            partes.append(f"<p>{obs}</p>")
        descricao = "".join(partes)
    else:
        descricao = str(des)

    # Area: V4 usa area_total; V5 mapeia para area (construida tem prioridade se existir)
    area = car.get('area_construida') or car.get('area_total') or 0

    # Parceiro: V4 tem proprietario + corretor_parceiro em captacao
    corr_parc = cap.get('corretor_parceiro', {}) if isinstance(cap, dict) else {}

    return {
        'titulo':          inf.get('titulo', ''),
        'slug':            inf.get('slug', slug_fallback),
        'tipo':            cla.get('tipo_principal', cla.get('tipo', '')),
        'finalidade':      cla.get('finalidade', 'venda'),
        'tipo_negocio':    cla.get('tipo_negocio', 'revendas'),
        'valor':           inf.get('valor', 0),
        'area':            area,
        'quartos':         car.get('quartos', 0),
        'banheiros':       car.get('banheiros', 0),
        'vagas':           car.get('vagas', 0),
        'bairro':          inf.get('bairro', ''),
        'cidade':          inf.get('cidade', 'Anapolis'),
        'estado':          inf.get('estado', 'GO'),
        'descricao':       descricao,
        'seo_title':       seo.get('titulo_seo', seo.get('title', '')),
        'seo_description': seo.get('descricao_seo', seo.get('description', '')),
        'foto_capa':       fot.get('foto_capa', '') if isinstance(fot, dict) else str(fot),
        'parceiro': {
            'nome':     corr_parc.get('nome', ''),
            'creci':    corr_parc.get('creci', ''),
            'whatsapp': corr_parc.get('whatsapp', ''),
        },
    }
