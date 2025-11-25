# 🤝 Guia de Contribuição - Montreal Weather ETL Dashboard

Bem-vindo! 🎉 Este documento contém diretrizes para contribuir com o projeto Montreal Weather ETL Dashboard.

## 📋 Código de Conduta

Este projeto segue um código de conduta para garantir um ambiente colaborativo e respeitoso. Ao participar, você concorda em:

- Ser respeitoso com todos os participantes
- Contribuir de forma construtiva
- Manter a qualidade do código e documentação
- Seguir as melhores práticas de desenvolvimento

## 🚀 Como Contribuir

### 1. Preparação do Ambiente

```bash
# Clone o repositório
git clone https://github.com/your-username/montreal-weather-etl.git
cd montreal-weather-etl

# Configure o ambiente
make setup
# ou manualmente:
cp .env.example .env
# Edite .env com sua chave da API OpenWeatherMap

# Execute o sistema
make up
```

### 2. Processo de Desenvolvimento

#### Fluxo de Trabalho Git
```
main (branch principal)
├── feature/nome-da-feature
├── bugfix/descricao-do-bug
├── docs/melhoria-documentacao
└── refactor/otimizacao-codigo
```

#### Commits Padronizados
```
feat: adicionar nova funcionalidade de cache
fix: corrigir erro na validação de dados
docs: atualizar documentação da API
refactor: otimizar consultas do banco de dados
test: adicionar testes para serviço de weather
chore: atualizar dependências
```

### 3. Padrões de Código

#### Rust
```bash
# Formatação
cargo fmt

# Linting
cargo clippy -- -D warnings

# Testes
cargo test
```

#### Python
```bash
# Formatação (se usar black)
black .

# Linting (se usar flake8)
flake8 .

# Testes (se usar pytest)
pytest
```

### 4. Testes

#### Tipos de Testes
- **Unitários**: Testam funções individuais
- **Integração**: Testam interação entre componentes
- **E2E**: Testam o fluxo completo
- **Performance**: Validam performance e escalabilidade

#### Executando Testes
```bash
# Testes Rust
make test

# Testes Python (quando implementados)
cd python_analytics && python -m pytest

# Cobertura de testes
cargo tarpaulin  # Para Rust
```

## 📝 Tipos de Contribuições

### 🐛 Correções de Bugs
1. Identifique o bug através dos logs ou issues
2. Reproduza o problema
3. Implemente a correção
4. Adicione testes para prevenir regressão
5. Atualize documentação se necessário

### ✨ Novas Funcionalidades
1. Abra uma issue descrevendo a funcionalidade
2. Discuta a implementação proposta
3. Implemente seguindo os padrões do projeto
4. Adicione testes abrangentes
5. Atualize documentação

### 📚 Melhorias na Documentação
1. Identifique lacunas ou imprecisões
2. Atualize README, CHANGELOG ou documentação específica
3. Mantenha consistência entre idiomas
4. Use linguagem clara e acessível

### 🔧 Refatoração
1. Identifique código duplicado ou complexo
2. Planeje a refatoração mantendo funcionalidade
3. Execute testes antes e depois
4. Documente mudanças significativas

## 🎯 Diretrizes Específicas

### Rust (ETL Service)

#### Estrutura de Código
```
src/
├── models/          # Structs e enums de dados
├── services/        # Lógica de negócio
├── config/          # Configuração da aplicação
├── utils/           # Funções utilitárias
└── main.rs          # Ponto de entrada
```

#### Boas Práticas
- Use `Result<T, E>` para tratamento de erros
- Implemente `Debug` e `Clone` quando apropriado
- Documente funções públicas com `///`
- Use logging apropriado (info!, warn!, error!)
- Mantenha funções pequenas e focadas

### Python (Analytics API)

#### Estrutura de Código
```
app/
├── api/             # Endpoints REST
├── models/          # Modelos de dados
├── services/        # Lógica de negócio
├── utils/           # Utilitários
└── templates/       # Templates HTML
```

#### Boas Práticas
- Use type hints em todas as funções
- Documente com docstrings
- Mantenha consistência com PEP 8
- Use blueprints para organização de rotas
- Implemente tratamento de erros adequado

### Docker

#### Dockerfile Guidelines
- Use multi-stage builds quando possível
- Minimize tamanho da imagem final
- Use `.dockerignore` apropriado
- Implemente health checks
- Use usuários não-privilegiados

### Banco de Dados

#### Migrações
- Documente todas as mudanças no schema
- Mantenha compatibilidade com versões anteriores
- Teste migrações em ambiente de desenvolvimento
- Use transações para mudanças críticas

## 🔍 Revisão de Código

### Checklist para Pull Requests
- [ ] Código compila sem erros
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Commits seguem convenção
- [ ] Não há código comentado desnecessário
- [ ] Variáveis e funções têm nomes descritivos
- [ ] Tratamento de erros adequado
- [ ] Logs apropriados adicionados

### Processo de Review
1. **Automated Checks**: CI/CD executa testes e linting
2. **Peer Review**: Pelo menos um maintainer revisa
3. **Integration Tests**: Validam integração entre componentes
4. **Merge**: Squash merge com mensagem descritiva

## 🐛 Reportando Issues

### Template para Bug Reports
```markdown
**Descrição**
Breve descrição do problema

**Para Reproduzir**
Passos para reproduzir:
1. Ir para '...'
2. Clicar em '....'
3. Ver erro

**Comportamento Esperado**
O que deveria acontecer

**Screenshots**
Se aplicável, adicione screenshots

**Ambiente**
- OS: [ex: Ubuntu 20.04]
- Docker: [ex: 24.0.1]
- Versão do projeto: [ex: v1.0.0]
```

### Template para Feature Requests
```markdown
**Resumo**
Breve descrição da funcionalidade

**Motivação**
Por que essa funcionalidade é necessária

**Solução Proposta**
Descrição da implementação sugerida

**Alternativas Consideradas**
Outras abordagens consideradas
```

## 📞 Comunicação

- **Issues**: Para bugs e solicitações de funcionalidades
- **Discussions**: Para questões gerais e ideias
- **Pull Requests**: Para submeter código
- **Email**: Para questões sensíveis ou privadas

## 🎖️ Reconhecimento

Contribuições são reconhecidas através de:
- Lista de contribuidores no README
- Créditos especiais para contribuições significativas
- Participação em decisões técnicas

## 📋 Licença

Ao contribuir, você concorda que suas contribuições estarão sob a mesma licença MIT do projeto.

---

**Obrigado por contribuir! 🙏**

Sua contribuição ajuda a tornar o Montreal Weather ETL Dashboard melhor para todos os usuários.
