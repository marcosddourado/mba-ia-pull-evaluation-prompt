"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data():
    data = load_prompts(str(PROMPT_FILE))
    return data[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado"
        assert prompt_data["system_prompt"].strip(), "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data.get("system_prompt", "")
        role_keywords = ["Você é", "você é", "Product Manager", "PM", "Assistente"]
        assert any(kw in system_prompt for kw in role_keywords), (
            "system_prompt não define uma persona/role. "
            "Inclua algo como 'Você é um Product Manager...'"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "")
        format_keywords = [
            "Como ", "eu quero", "para que",
            "Critérios de Aceitação", "Dado que", "Quando", "Então",
            "User Story", "Markdown"
        ]
        assert any(kw in system_prompt for kw in format_keywords), (
            "system_prompt não especifica o formato de User Story ou Markdown. "
            "Inclua o template 'Como [X], eu quero [Y], para que [Z]' e Critérios de Aceitação."
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        # Aceita few-shot no system_prompt OU como lista few_shot_examples
        has_inline = (
            "Exemplo" in prompt_data.get("system_prompt", "") or
            "exemplo" in prompt_data.get("system_prompt", "")
        )
        has_structured = (
            "few_shot_examples" in prompt_data and
            isinstance(prompt_data["few_shot_examples"], list) and
            len(prompt_data["few_shot_examples"]) > 0
        )
        assert has_inline or has_structured, (
            "Não foram encontrados exemplos Few-shot. "
            "Adicione exemplos no system_prompt ou na chave 'few_shot_examples'."
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que não há nenhum [TODO] esquecido no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        full_text = system_prompt + user_prompt
        assert "[TODO]" not in full_text, (
            "Encontrado '[TODO]' no prompt. Remova ou substitua antes de publicar."
        )

    def test_minimum_techniques(self, prompt_data):
        """Verifica se pelo menos 2 técnicas foram listadas nos metadados."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas em 'techniques_applied', "
            f"encontradas: {len(techniques)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
