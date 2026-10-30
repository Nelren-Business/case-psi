import json
import os
from datetime import datetime, timedelta

ARQUIVO_JSON = 'src/data/propostas.json'

def carregar_dados():
    if not os.path.exists(ARQUIVO_JSON):
        return []
    with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_dados(dados):
    # Cria a pasta src/data caso ela não exista
    os.makedirs(os.path.dirname(ARQUIVO_JSON), exist_ok=True)
    
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def criar_proposta():
    print("🚀 --- Gerador de Propostas Nelren-Business ---")
    slug = input("1. Nome da URL (ex: marcos-silva): ").strip().lower()
    nome = input("2. Nome do Cliente (ex: Marcos Silva): ").strip()
    
    try:
        dias_validade = int(input("3. Quantos dias de validade a proposta tem? (ex: 7): "))
    except ValueError:
        print("❌ Erro: Por favor, digite apenas números inteiros para os dias.")
        return

    # Calcula a data e joga para o final do dia (23:59:59)
    data_expiracao = datetime.now() + timedelta(days=dias_validade)
    data_expiracao_final_do_dia = data_expiracao.replace(hour=23, minute=59, second=59, microsecond=0)
    
    # Formata no padrão ISO (que o JavaScript entende perfeitamente)
    data_formatada = data_expiracao_final_do_dia.isoformat()

    dados = carregar_dados()
    
    # Remove se já existir uma proposta com a mesma URL (para atualizar)
    dados = [d for d in dados if d['slug'] != slug]
    
    nova_proposta = {
        "slug": slug,
        "nome": nome,
        "validade": data_formatada
    }
    
    dados.append(nova_proposta)
    salvar_dados(dados)
    
    print(f"\n✅ Sucesso! Proposta criada para {nome}.")
    print(f"🔗 URL local: http://localhost:4321/psi/{slug}")
    print(f"⏳ Expira em: {data_expiracao_final_do_dia.strftime('%d/%m/%Y às %H:%M')}")

if __name__ == "__main__":
    criar_proposta()