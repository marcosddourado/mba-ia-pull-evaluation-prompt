"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt bug_to_user_story_v1 do LangSmith Hub e salva localmente.
    """
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return False

    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    print(f"Puxando prompt: {prompt_name} ...")

    prompt = hub.pull(prompt_name)
    print("✓ Prompt carregado com sucesso")

    system_msg = ""
    user_msg = ""

    for message in prompt.messages:
        class_name = message.__class__.__name__
        template = message.prompt.template if hasattr(message, "prompt") else ""

        if class_name == "SystemMessagePromptTemplate":
            system_msg = template
        elif class_name == "HumanMessagePromptTemplate":
            user_msg = template

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_msg,
            "user_prompt": user_msg,
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"
    if save_yaml(data, str(output_path)):
        print(f"✓ Salvo em: {output_path}")
        return True

    return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
