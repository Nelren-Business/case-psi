import json
import os
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any

ARQUIVO_JSON = 'src/data/propostas.json'

def carregar_dados() -> List[Dict[str, Any]]:
    if not os.path.exists(ARQUIVO_JSON):
        return []
    try:
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def salvar_dados(dados: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(ARQUIVO_JSON), exist_ok=True)
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def formatar_moeda(entrada: str) -> str:
    """Formata uma string ou número para o padrão R$ 0.000,00"""
    entrada_limpa = str(entrada).replace("R$", "").replace(" ", "")
    if "." in entrada_limpa and "," in entrada_limpa:
        entrada_limpa = entrada_limpa.replace(".", "").replace(",", ".")
    elif "," in entrada_limpa:
        entrada_limpa = entrada_limpa.replace(",", ".")
    
    try:
        valor = float(entrada_limpa)
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except ValueError:
        return str(entrada)

def obter_input_moeda(mensagem: str) -> str:
    while True:
        entrada = input(mensagem).strip()
        if not entrada:
            print("❌ O valor não pode ficar em branco.")
            continue
        return formatar_moeda(entrada)

def obter_input_inteiro(mensagem: str) -> int:
    while True:
        try:
            valor = int(input(mensagem).strip())
            if valor <= 0:
                print("❌ O número de dias deve ser maior que zero.")
                continue
            return valor
        except ValueError:
            print("❌ Digite apenas números inteiros (ex: 7).")

def processar_proposta(slug: str, nome: str, preco_investimento: str, orcamento_ads: str, dias_validade: int) -> None:
    """Lógica central isolada para ser consumida tanto via CLI quanto interativo."""
    preco_formatado = formatar_moeda(preco_investimento)
    orcamento_formatado = formatar_moeda(orcamento_ads)
    
    data_expiracao = datetime.now() + timedelta(days=dias_validade)
    data_expiracao_final = data_expiracao.replace(hour=23, minute=59, second=59, microsecond=0)
    data_formatada = data_expiracao_final.isoformat()

    dados = carregar_dados()
    dados = [d for d in dados if d.get('slug') != slug]
    
    nova_proposta = {
        "slug": slug,
        "nome": nome,
        "validade": data_formatada,
        "textoIntroducao": "",
        "textoInvestimentoInicial": "",
        "PreçoInvestimentoInicial": preco_formatado,
        "OrçamentoAdsMensal": orcamento_formatado,
        "ValidadeProposta": f"{dias_validade} dias"
    }
    
    dados.append(nova_proposta)
    salvar_dados(dados)
    
    print(f"\n✅ Proposta salva com sucesso para {nome}!")
    print(f"🔗 URL local: http://localhost:4321/psi/{slug}")
    print(f"💼 Investimento Inicial: {preco_formatado}")
    print(f"📢 Ads Mensal: {orcamento_formatado}")
    print(f"⏳ Validade: {dias_validade} dias (Até {data_expiracao_final.strftime('%d/%m/%Y às %H:%M')})")

def criar_proposta_interativa() -> None:
    print("🚀 --- Gerador de Propostas Nelren-Business ---")
    slug = input("1. Nome da URL (ex: hash): ").strip().lower()
    nome = input("2. Nome do Cliente (ex: Marcos Silva): ").strip()
    preco = obter_input_moeda("3. Preço do Investimento Inicial (ex: 5000): ")
    orcamento = obter_input_moeda("4. Orçamento em Ads Mensal (ex: 1500): ")
    dias = obter_input_inteiro("5. Validade da proposta em dias (ex: 7): ")
    
    if slug and nome:
        processar_proposta(slug, nome, preco, orcamento, dias)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador automático de propostas.")
    parser.add_argument("--slug", type=str, help="Hash da URL")
    parser.add_argument("--nome", type=str, help="Nome do contato")
    parser.add_argument("--preco", type=str, help="Preço de investimento inicial")
    parser.add_argument("--orcamento", type=str, help="Orçamento mensal ADS")
    parser.add_argument("--validade", type=int, help="Dias de validade")
    
    args = parser.parse_args()

    # Se todos os argumentos forem passados, roda em modo Headless (Automático via Webhook)
    if args.slug and args.nome and args.preco and args.orcamento and args.validade:
        processar_proposta(args.slug, args.nome, args.preco, args.orcamento, args.validade)
    else:
        # Modo fallback caso execute manualmente com duplo clique ou no terminal sem argumentos
        criar_proposta_interativa()