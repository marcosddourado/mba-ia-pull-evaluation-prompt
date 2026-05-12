"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts de prompts/bug_to_user_story_v1.yml (ou v2.yml)
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import HumanMessage, AIMessage
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    if not prompt_data.get("system_prompt", "").strip():
        errors.append("system_prompt está vazio")

    if not prompt_data.get("user_prompt", "").strip():
        errors.append("user_prompt está vazio")

    if "TODO" in prompt_data.get("system_prompt", ""):
        errors.append("system_prompt ainda contém TODOs não preenchidos")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome completo do prompt (ex: marcosdourado92/bug_to_user_story_v1)
        prompt_data: Dados do prompt carregados do YAML

    Returns:
        True se sucesso, False caso contrário
    """
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print(f"❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return False

    system_prompt = prompt_data["system_prompt"]
    user_prompt = prompt_data["user_prompt"]
    few_shot_examples = prompt_data.get("few_shot_examples", [])

    messages = [SystemMessagePromptTemplate.from_template(system_prompt)]
    for example in few_shot_examples:
        messages.append(HumanMessage(content=example["input"]))
        messages.append(AIMessage(content=example["output"]))
    messages.append(HumanMessagePromptTemplate.from_template(user_prompt))

    prompt = ChatPromptTemplate.from_messages(messages)

    print(f"   Fazendo push: {prompt_name} ...")
    try:
        hub.push(prompt_name, prompt, new_repo_is_public=True)
        print(f"   ✓ Push concluído: {prompt_name}")
    except Exception as e:
        if "Nothing to commit" in str(e) or "409" in str(e):
            print(f"   ✓ Sem alterações: {prompt_name} já está atualizado no hub")
        else:
            raise
    return True


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompts_dir = Path(__file__).parent.parent / "prompts"

    print_section_header("PUSH DE PROMPTS AO LANGSMITH HUB")

    prompts_to_push = [
        ("bug_to_user_story_v1", prompts_dir / "bug_to_user_story_v1.yml"),
        ("bug_to_user_story_v2", prompts_dir / "bug_to_user_story_v2.yml"),
    ]

    success_count = 0
    for prompt_key, yaml_path in prompts_to_push:
        if not yaml_path.exists():
            print(f"⚠️  Arquivo não encontrado, pulando: {yaml_path.name}")
            continue

        data = load_yaml(str(yaml_path))
        if not data or prompt_key not in data:
            print(f"❌ Chave '{prompt_key}' não encontrada em {yaml_path.name}")
            continue

        prompt_name = f"{username}/{prompt_key}"
        if push_prompt_to_langsmith(prompt_name, data[prompt_key]):
            success_count += 1

    if success_count == 0:
        print("\n❌ Nenhum prompt foi publicado com sucesso.")
        return 1

    print(f"\n✅ {success_count} prompt(s) publicado(s).")
    print(f"   Confira em: https://smith.langchain.com/hub/{username}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
