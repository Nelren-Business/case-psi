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

def obter_input_texto(mensagem: str) -> str:
    """Obtém um texto sem aplicar nenhuma formatação."""
    while True:
        entrada = input(mensagem).strip()
        if not entrada:
            print("❌ O valor não pode ficar em branco.")
            continue
        return entrada

def obter_input_inteiro(mensagem: str) -> int:
    """Solicita e valida um número inteiro positivo."""
    while True:
        try:
            valor = int(input(mensagem).strip())
            if valor <= 0:
                print("❌ O número deve ser maior que zero.")
                continue
            return valor
        except ValueError:
            print("❌ Digite apenas números inteiros (ex: 7).")

def processar_proposta(slug: str, nome: str, preco_investimento: str, orcamento_ads: str, dias_validade: int, validade_proposta: int) -> None:
    """Lógica central: recebe e salva os dados puros (crus) vindos do banco ou terminal."""
    
    # O valor inteiro de dias_validade é usado SOMENTE para o cálculo real de expiração da página
    data_expiracao = datetime.now() + timedelta(days=dias_validade)
    data_expiracao_final = data_expiracao.replace(hour=23, minute=59, second=59, microsecond=0)
    data_formatada = data_expiracao_final.isoformat()

    dados = carregar_dados()
    
    # Remove duplicadas por slug para atualização idempotente
    dados = [d for d in dados if d.get('slug') != slug]
    
    nova_proposta = {
        "slug": slug,
        "nome": nome,
        "validade": data_formatada,
        "textoIntroducao": "",
        "textoInvestimentoInicial": "",
        "PreçoInvestimentoInicial": str(preco_investimento),  
        "OrçamentoAdsMensal": str(orcamento_ads),             
        "ValidadeProposta": str(validade_proposta) # Valor comercial exibido no site
    }
    
    dados.append(nova_proposta)
    salvar_dados(dados)
    
    print(f"\n✅ Proposta salva com sucesso para {nome}!")
    print(f"🔗 URL local: http://localhost:4321/psi/{slug}")
    print(f"💼 Investimento Inicial: {preco_investimento}")
    print(f"📢 Ads Mensal: {orcamento_ads}")
    print(f"⏳ Tempo de Página: {dias_validade} dias (Até {data_expiracao_final.strftime('%d/%m/%Y às %H:%M')})")
    print(f"👁️ Validade no Site: {validade_proposta}")

def criar_proposta_interativa() -> None:
    print("🚀 --- Gerador de Propostas Nelren-Business ---")
    slug = obter_input_texto("1. Nome da URL (ex: hash): ").lower()
    nome = obter_input_texto("2. Nome do Cliente (ex: Marcos Silva): ")
    preco = obter_input_texto("3. Preço do Investimento Inicial (ex: 1.950): ")
    orcamento = obter_input_texto("4. Orçamento em Ads Mensal (ex: 180): ")
    dias = obter_input_inteiro("5. Tempo da página no ar em dias (ex: 7): ")
    val_proposta = obter_input_inteiro("6. Validade da proposta mostrada no site (ex: 7): ")
    
    if slug and nome:
        processar_proposta(slug, nome, preco, orcamento, dias, val_proposta)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador automático de propostas.")
    parser.add_argument("--slug", type=str, help="Hash da URL")
    parser.add_argument("--nome", type=str, help="Nome do contato")
    parser.add_argument("--preco", type=str, help="Preço de investimento inicial")
    parser.add_argument("--orcamento", type=str, help="Orçamento mensal ADS")
    parser.add_argument("--validade", type=int, help="Dias de validade técnica da página")
    parser.add_argument("--validade_proposta", type=int, help="Dias de validade comercial mostrada no site")
    
    args = parser.parse_args()

    # Verifica se TODOS os argumentos foram passados para rodar via Webhook
    if args.slug and args.nome and args.preco and args.orcamento and args.validade and args.validade_proposta:
        processar_proposta(args.slug, args.nome, args.preco, args.orcamento, args.validade, args.validade_proposta)
    else:
        # Fallback manual
        criar_proposta_interativa()