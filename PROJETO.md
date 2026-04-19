# PROJETO: Marcos Rosa — Negócios Imobiliários
> Caderno de bordo centralizado. Cole este arquivo no início de cada sessão Claude.
> Última atualização: 05/03/2026

---

## 🧠 CONTEXTO GERAL

**Profissional:** Marcos Rosa Campos  
**CRECI:** CRECI-GO 35088-F (jun/2022)  
**Localização:** Anápolis, Goiás, Brasil  
**WhatsApp:** (62) 98114-8448  
**E-mail:** mrcimoveis78@gmail.com  
**Site:** imovflow.com.br  

---

## 🖥️ INFRAESTRUTURA

| Item | Detalhe |
|------|---------|
| Hospedagem | KingHost |
| Servidor | 191.6.209.223 |
| Usuário SSH | imovflow |
| Pasta WordPress | ~/www |
| Pasta Tema | ~/www/wp-content/themes/marcos-rosa |
| Tema ativo | marcos-rosa v1.0.0 (customizado) |
| GitHub | https://github.com/socramasor12-sudo/imovflow-site |
| Git identity servidor | mrcimoveis78@gmail.com / Marcos Rosa |

---

## ✅ CONCLUÍDO

- [x] Rebrand IMOVFLOW → Marcos Rosa (118 substituições banco + arquivos)
- [x] "Mr. Marcos Rosa" corrigido para "Marcos Rosa" em todo o site
- [x] Tema WordPress customizado criado e deployado
- [x] Logo MR dourada em header, hero e footer
- [x] Foto P&B (camisa + gravata) na seção Sobre
- [x] Seção de captação de imóveis com formulário AJAX
- [x] WhatsApp flutuante ativo (62) 98114-8448
- [x] GitHub sincronizado com servidor
- [x] Token PAT e git identity configurados no servidor
- [x] Cache LiteSpeed limpo

---

## 🔄 PRÓXIMOS PASSOS

1. **Visual** — Corrigir hero: logo sobreposta ao conteúdo (z-index/grid)
2. **SEO** — Yoast: título + meta descrição + Open Graph
3. **Imóveis** — CPT imovel + cadastrar primeiros lançamentos
4. **Automações** — Formulário captação → email + WhatsApp automático
5. **Marketing** — Google Meu Negócio + Instagram bio atualizada

---

## 📋 COMANDOS ESSENCIAIS SSH

```bash
# Conectar
ssh imovflow@191.6.209.223

# Push tema para GitHub
git -C ~/www/wp-content/themes/marcos-rosa add .
git -C ~/www/wp-content/themes/marcos-rosa commit -m "descrição"
git -C ~/www/wp-content/themes/marcos-rosa push origin master

# Limpar cache
cd ~/www && wp cache flush --allow-root

# Substituição em massa
cd ~/www && wp search-replace 'ANTIGO' 'NOVO' --allow-root
--azul:          #1a2744
--azul-medio:    #243457
--dourado:       #c9a84c
--dourado-claro: #e2c97e
--branco:        #f8f6f1
--cinza-claro:   #edeae3

Títulos: Cormorant Garamond (serif)
Corpo:   Josefin Sans (sans-serif)