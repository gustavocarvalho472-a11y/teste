// P0.1 - Interface TypeScript para Oportunidade

export interface OportunidadeData {
  // Identificação
  municipio: string;
  estado: string;
  categoria: string;
  nivel: 'PREMIUM' | 'FORTE' | 'BOA';

  // Orçamento
  orcamento: {
    total: number;           // R$ 3.080.000.000 (média histórica)
    executado: number;       // R$ 950.000.000 (até maio)
    disponivel: number;      // R$ 2.450.000.000 (calculado)
    percentualExecutado: number; // 20.8%
    percentualDisponivel: number; // 79.2%
  };

  // Contratos
  contratos: {
    fechados: number;        // 1.200 (até maio)
    mediaAnual: number;      // 4.320
    esperadoAteMes: number;  // 1.728
    gap: number;             // -528
    gapPercentual: number;   // -30.6%
    projecaoAno: number;     // 3.000
  };

  // Oportunidades
  oportunidades: {
    editaisAtivos: number;         // 285
    valorEditais: number;          // R$ 1.200.000.000
    orcamentoLivre: number;        // R$ 1.250.000.000
    diferencaFinanceira: number;   // R$ 280.000.000
    diferencaFinanceiraPercent: number; // -22.8%
  };

  // Histórico (para dropdown)
  historico: Array<{
    ano: number;
    contratos: number;
    valorExecutado: number;
    ticketMedio: number;
  }>;

  // Comparação
  comparacao: {
    esperadoContratos: number;     // 1.728
    realContratos: number;         // 1.200
    esperadoValor: number;         // R$ 1.230.000.000
    realValor: number;             // R$ 950.000.000
  };
}

export interface DadosHistoricos {
  municipio: string;
  estado: string;
  categoria: string;

  historico: Array<{
    ano: number;
    totalContratos: number;
    valorExecutado: number;
  }>;

  anoAtual: {
    fechados: number;
    executado: number;
    editaisAtivos: {
      quantidade: number;
      valor: number;
    };
  };
}

// Cores por nível
export const OPPORTUNITY_COLORS = {
  PREMIUM: {
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    primary: '#10b981',
    light: '#d1fae5',
    text: '#065f46',
    border: '#34d399'
  },
  FORTE: {
    gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    primary: '#3b82f6',
    light: '#dbeafe',
    text: '#1e40af',
    border: '#60a5fa'
  },
  BOA: {
    gradient: 'linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)',
    primary: '#7c3aed',
    light: '#f3e8ff',
    text: '#5b21b6',
    border: '#a78bfa'
  }
} as const;
