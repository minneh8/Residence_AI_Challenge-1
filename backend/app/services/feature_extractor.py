import re
import string


FEATURE_NAMES = [
    'tamanho_medio_palavra', 'num_palavras', 'pct_erro_ortografico',
    'types_proporcao', 'fontes_proporcao', 'estudos_previos_proporcao',
    'emotividade', 'sensacionalismo_proporcao', 'verbos_proporcao',
    'verbos_subj_imp_proporcao', 'substantivos_proporcao',
    'adjetivos_proporcao', 'adverbios_proporcao', 'modais_proporcao',
    'pronomes_proporcao', 'pausalidade', 'indice_legibilidade',
    'tamanho_medio_frase',
]

SENSATIONAL_WORDS = {'urgente', 'chocante', 'inacreditável', 'exclusivo', 'bomba', 'alerta'}
MODAL_WORDS = {'pode', 'poderia', 'deve', 'deveria', 'talvez', 'possível', 'possivelmente'}
SOURCE_WORDS = {'fonte', 'estudo', 'pesquisa', 'dados', 'segundo', 'relatório', 'instituto'}


def _words(text: str) -> list[str]:
    return re.findall(r"\b[\wÀ-ÿ]+\b", text.lower())


def _sentences(text: str) -> list[str]:
    return [item.strip() for item in re.split(r'[.!?]+', text) if item.strip()]


def extract_features(text: str) -> dict[str, float]:
    if not text or len(text.strip()) < 20:
        raise ValueError('O texto deve possuir pelo menos 20 caracteres.')

    words = _words(text)
    sentences = _sentences(text)
    total_words = max(len(words), 1)
    total_chars = max(len(text), 1)
    lengths = [len(word) for word in words] or [0]
    unique_words = len(set(words))
    punctuation = sum(char in string.punctuation for char in text)
    sensational = sum(word in SENSATIONAL_WORDS for word in words)
    modal = sum(word in MODAL_WORDS for word in words)
    source = sum(word in SOURCE_WORDS for word in words)
    uppercase_words = sum(word.isupper() and len(word) > 2 for word in text.split())
    exclamations = text.count('!')

    return {
        'tamanho_medio_palavra': sum(lengths) / total_words,
        'num_palavras': float(len(words)),
        'pct_erro_ortografico': 0.0,
        'types_proporcao': unique_words / total_words,
        'fontes_proporcao': source / total_words,
        'estudos_previos_proporcao': 0.0,
        'emotividade': min((exclamations + uppercase_words) / total_words, 1.0),
        'sensacionalismo_proporcao': sensational / total_words,
        'verbos_proporcao': 0.0,
        'verbos_subj_imp_proporcao': 0.0,
        'substantivos_proporcao': 0.0,
        'adjetivos_proporcao': 0.0,
        'adverbios_proporcao': 0.0,
        'modais_proporcao': modal / total_words,
        'pronomes_proporcao': 0.0,
        'pausalidade': punctuation / total_chars,
        'indice_legibilidade': min(max(1.0 - (sum(lengths) / total_words) / 15.0, 0.0), 1.0),
        'tamanho_medio_frase': len(words) / max(len(sentences), 1),
    }
