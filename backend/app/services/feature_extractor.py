import re
import string

try:
    import spacy
except ImportError:
    spacy = None

FEATURE_NAMES = [
    'tamanho_medio_palavra', 'pct_erro_ortografico',
    'fontes_proporcao', 'estudos_previos_proporcao', 'emotividade',
    'sensacionalismo_proporcao', 'verbos_proporcao',
    'verbos_subj_imp_proporcao', 'substantivos_proporcao',
    'adjetivos_proporcao', 'adverbios_proporcao', 'modais_proporcao',
    'pronomes_proporcao', 'pausalidade', 'indice_legibilidade',
    'tamanho_medio_frase',
]

SENSATIONAL_WORDS = {'urgente', 'chocante', 'inacreditável', 'exclusivo', 'bomba', 'alerta'}
MODAL_WORDS = {'pode', 'poderia', 'deve', 'deveria', 'talvez', 'possível', 'possivelmente'}
SOURCE_WORDS = {'fonte', 'estudo', 'pesquisa', 'dados', 'segundo', 'relatório', 'instituto'}


def _words(text: str) -> list[str]:
    return re.findall(r'\b[\wÀ-ÿ]+\b', text.lower())


def _load_nlp():
    if spacy is None:
        return None
    try:
        return spacy.load('pt_core_news_sm')
    except Exception:
        return None


NLP = _load_nlp()


def extract_features(text: str) -> dict[str, float]:
    if not text or len(text.strip()) < 20:
        raise ValueError('O texto deve possuir pelo menos 20 caracteres.')

    words = _words(text)
    total = max(len(words), 1)
    sentences = [part for part in re.split(r'[.!?]+', text) if part.strip()]
    lengths = [len(word) for word in words] or [0]
    punctuation = sum(char in string.punctuation for char in text)
    upper = sum(word.isupper() and len(word) > 2 for word in text.split())
    exclamations = text.count('!')

    result = {
        'tamanho_medio_palavra': sum(lengths) / total,
        'pct_erro_ortografico': 0.0,
        'fontes_proporcao': sum(word in SOURCE_WORDS for word in words) / total,
        'estudos_previos_proporcao': sum(word in {'estudo', 'pesquisa', 'artigo', 'análise'} for word in words) / total,
        'emotividade': min((upper + exclamations) / total, 1.0),
        'sensacionalismo_proporcao': sum(word in SENSATIONAL_WORDS for word in words) / total,
        'verbos_proporcao': 0.0,
        'verbos_subj_imp_proporcao': 0.0,
        'substantivos_proporcao': 0.0,
        'adjetivos_proporcao': 0.0,
        'adverbios_proporcao': 0.0,
        'modais_proporcao': sum(word in MODAL_WORDS for word in words) / total,
        'pronomes_proporcao': 0.0,
        'pausalidade': punctuation / max(len(text), 1),
        'indice_legibilidade': min(max(1.0 - (sum(lengths) / total) / 15.0, 0.0), 1.0),
        'tamanho_medio_frase': len(words) / max(len(sentences), 1),
    }

    if NLP is not None:
        doc = NLP(text)
        tokens = [token for token in doc if not token.is_space and not token.is_punct]
        total_tokens = max(len(tokens), 1)
        result.update({
            'verbos_proporcao': sum(token.pos_ in {'VERB', 'AUX'} for token in tokens) / total_tokens,
            'substantivos_proporcao': sum(token.pos_ == 'NOUN' for token in tokens) / total_tokens,
            'adjetivos_proporcao': sum(token.pos_ == 'ADJ' for token in tokens) / total_tokens,
            'adverbios_proporcao': sum(token.pos_ == 'ADV' for token in tokens) / total_tokens,
            'pronomes_proporcao': sum(token.pos_ == 'PRON' for token in tokens) / total_tokens,
            'verbos_subj_imp_proporcao': sum(token.pos_ in {'VERB', 'AUX'} and any(mood in {'Sub', 'Imp'} for mood in token.morph.get('Mood')) for token in tokens) / total_tokens,
        })

    return result
