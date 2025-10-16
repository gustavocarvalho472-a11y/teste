# 📡 API de Oportunidades Comerciais

Documentação completa da API REST para consulta de oportunidades em licitações municipais.

## Base URL

```
http://localhost:3000/api
```

---

## Endpoints

### 1. GET `/api/oportunidades`

Lista todas as oportunidades com filtros opcionais.

#### Query Parameters

| Parâmetro | Tipo | Obrigatório | Padrão | Descrição |
|-----------|------|-------------|---------|-----------|
| `categoria` | string | Não | `TODOS` | Filtra por categoria (Educação, Saúde, etc) |
| `nivel` | string | Não | `TODOS` | Filtra por nível (PREMIUM, FORTE, BOA) |
| `estado` | string | Não | `TODOS` | Filtra por UF (SP, RJ, MG, etc) |
| `limit` | number | Não | `50` | Limita quantidade de resultados |

#### Exemplo de Request

```bash
curl "http://localhost:3000/api/oportunidades?nivel=PREMIUM&categoria=Educacao&limit=10"
```

#### Exemplo de Response (200 OK)

```json
{
  "success": true,
  "data": [
    {
      "municipio": "São Paulo",
      "estado": "SP",
      "categoria": "Educação",
      "nivel": "PREMIUM",
      "orcamento": {
        "total": 3080000000,
        "executado": 950000000,
        "disponivel": 2450000000,
        "percentualExecutado": 20.8,
        "percentualDisponivel": 79.2
      },
      "contratos": {
        "fechados": 1200,
        "mediaAnual": 4320,
        "esperadoAteMes": 1728,
        "gap": -528,
        "gapPercentual": -30.6,
        "projecaoAno": 3000
      },
      "oportunidades": {
        "editaisAtivos": 285,
        "valorEditais": 1200000000,
        "orcamentoLivre": 1250000000,
        "diferencaFinanceira": 280000000,
        "diferencaFinanceiraPercent": -22.8
      },
      "historico": [
        {
          "ano": 2020,
          "contratos": 4200,
          "valorExecutado": 2900000000,
          "ticketMedio": 690476
        }
      ],
      "comparacao": {
        "esperadoContratos": 1728,
        "realContratos": 1200,
        "esperadoValor": 1230000000,
        "realValor": 950000000
      }
    }
  ],
  "pagination": {
    "total": 6,
    "limit": 50,
    "showing": 6
  },
  "stats": {
    "totalMunicipios": 6,
    "orcamentoDisponivel": 8450000000,
    "orcamentoTotal": 12000000000,
    "editaisTotais": 1000,
    "valorEditais": 5200000000,
    "contratosFechados": 5750,
    "breakdown": {
      "premium": 2,
      "forte": 3,
      "boa": 1
    }
  },
  "metadata": {
    "categoria": "TODOS",
    "nivel": "PREMIUM",
    "estado": "TODOS",
    "dataAtualizacao": "2025-10-15T10:30:00.000Z",
    "versao": "1.0.0"
  }
}
```

#### Exemplo de Response - Erro (500)

```json
{
  "success": false,
  "error": "Erro ao processar oportunidades",
  "message": "Database connection failed"
}
```

---

### 2. POST `/api/oportunidades`

Busca uma oportunidade específica por município.

#### Request Body

```json
{
  "municipio": "São Paulo"
}
```

#### Exemplo de Request

```bash
curl -X POST http://localhost:3000/api/oportunidades \
  -H "Content-Type: application/json" \
  -d '{"municipio":"São Paulo"}'
```

#### Exemplo de Response (200 OK)

```json
{
  "success": true,
  "data": {
    "municipio": "São Paulo",
    "estado": "SP",
    "categoria": "Educação",
    "nivel": "PREMIUM",
    "orcamento": { ... },
    "contratos": { ... },
    "oportunidades": { ... },
    "historico": [ ... ],
    "comparacao": { ... }
  },
  "metadata": {
    "dataAtualizacao": "2025-10-15T10:30:00.000Z"
  }
}
```

#### Exemplo de Response - Não Encontrado (404)

```json
{
  "success": false,
  "error": "Município não encontrado"
}
```

#### Exemplo de Response - Bad Request (400)

```json
{
  "success": false,
  "error": "Município não especificado"
}
```

---

## Modelos de Dados

### OportunidadeData

```typescript
interface OportunidadeData {
  // Identificação
  municipio: string;
  estado: string;
  categoria: string;
  nivel: 'PREMIUM' | 'FORTE' | 'BOA';

  // Orçamento
  orcamento: {
    total: number;
    executado: number;
    disponivel: number;
    percentualExecutado: number;
    percentualDisponivel: number;
  };

  // Contratos
  contratos: {
    fechados: number;
    mediaAnual: number;
    esperadoAteMes: number;
    gap: number;
    gapPercentual: number;
    projecaoAno: number;
  };

  // Oportunidades
  oportunidades: {
    editaisAtivos: number;
    valorEditais: number;
    orcamentoLivre: number;
    diferencaFinanceira: number;
    diferencaFinanceiraPercent: number;
  };

  // Histórico
  historico: Array<{
    ano: number;
    contratos: number;
    valorExecutado: number;
    ticketMedio: number;
  }>;

  // Comparação
  comparacao: {
    esperadoContratos: number;
    realContratos: number;
    esperadoValor: number;
    realValor: number;
  };
}
```

---

## Níveis de Oportunidade

| Nível | Critério | Descrição |
|-------|----------|-----------|
| **PREMIUM** | Gap ≤ -30% | Municípios com execução muito abaixo da média histórica |
| **FORTE** | -30% < Gap ≤ -15% | Municípios com execução moderadamente abaixo da média |
| **BOA** | Gap > -15% | Municípios com execução levemente abaixo da média |

**Gap** = (Contratos Fechados - Esperado até o Mês) / Esperado até o Mês * 100

---

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| `200` | Sucesso |
| `400` | Requisição inválida (parâmetros faltando ou incorretos) |
| `404` | Recurso não encontrado |
| `500` | Erro interno do servidor |

---

## Rate Limiting

Atualmente não há rate limiting implementado. Em produção, recomenda-se:

- **100 requests/minuto** por IP para GET
- **20 requests/minuto** por IP para POST

---

## Exemplos de Uso

### JavaScript/Fetch

```javascript
// Buscar todas as oportunidades PREMIUM
const response = await fetch('/api/oportunidades?nivel=PREMIUM');
const data = await response.json();

if (data.success) {
  console.log(`Encontradas ${data.pagination.total} oportunidades`);
  console.log(`Orçamento disponível: R$ ${data.stats.orcamentoDisponivel}`);
}
```

### JavaScript/Axios

```javascript
import axios from 'axios';

// Buscar oportunidade específica
const response = await axios.post('/api/oportunidades', {
  municipio: 'São Paulo'
});

console.log(response.data.data.orcamento.disponivel);
```

### Python/Requests

```python
import requests

# Buscar oportunidades por categoria
response = requests.get(
    'http://localhost:3000/api/oportunidades',
    params={'categoria': 'Saúde', 'limit': 20}
)

data = response.json()
print(f"Total: {data['pagination']['total']}")
```

### cURL

```bash
# GET com filtros
curl -G "http://localhost:3000/api/oportunidades" \
  --data-urlencode "categoria=Educação" \
  --data-urlencode "estado=SP" \
  --data-urlencode "nivel=PREMIUM"

# POST buscar município
curl -X POST http://localhost:3000/api/oportunidades \
  -H "Content-Type: application/json" \
  -d '{"municipio":"Rio de Janeiro"}'
```

---

## Versionamento

API atual: **v1.0.0**

Futuras versões serão acessíveis via:
- `/api/v2/oportunidades`
- Header: `Accept-Version: 2.0.0`

---

## Roadmap

- [ ] Autenticação JWT
- [ ] Webhooks para novas oportunidades
- [ ] Filtros avançados (range de valores, data)
- [ ] Exportação CSV/Excel
- [ ] GraphQL endpoint
- [ ] WebSocket para atualizações em tempo real
- [ ] Cache Redis
- [ ] Documentação Swagger/OpenAPI

---

## Suporte

Para dúvidas ou problemas, abra uma issue no repositório.
