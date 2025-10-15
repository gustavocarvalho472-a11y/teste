// P0.2 - Função de Cálculo de Oportunidades

import { OportunidadeData, DadosHistoricos } from '../types/oportunidade';

export function calcularOportunidade(dados: DadosHistoricos): OportunidadeData {
  // 1. Média histórica (2020-2024)
  const mediaContratos = dados.historico.reduce((acc, h) => acc + h.totalContratos, 0) / dados.historico.length;
  const mediaValor = dados.historico.reduce((acc, h) => acc + h.valorExecutado, 0) / dados.historico.length;

  // 2. Ajuste sazonal (maio = 5/12 do ano)
  const fatorSazonal = 5 / 12;
  const esperadoContratos = mediaContratos * fatorSazonal;
  const esperadoValor = mediaValor * fatorSazonal;

  // 3. Disponível
  const disponivel = mediaValor - dados.anoAtual.executado;
  const percentualExecutado = (dados.anoAtual.executado / mediaValor) * 100;
  const percentualDisponivel = 100 - percentualExecutado;

  // 4. Gap
  const gapContratos = dados.anoAtual.fechados - esperadoContratos;
  const gapPercentual = (gapContratos / esperadoContratos) * 100;

  // 5. Projeção anual
  const projecaoAno = dados.anoAtual.fechados / fatorSazonal;

  // 6. Diferença financeira
  const diferencaFinanceira = dados.anoAtual.executado - esperadoValor;
  const diferencaFinanceiraPercent = (diferencaFinanceira / esperadoValor) * 100;

  // 7. Orçamento livre (sem edital)
  const orcamentoLivre = disponivel - dados.anoAtual.editaisAtivos.valor;

  // 8. Determinar nível de oportunidade
  let nivel: 'PREMIUM' | 'FORTE' | 'BOA';
  if (gapPercentual <= -30) {
    nivel = 'PREMIUM';
  } else if (gapPercentual <= -15) {
    nivel = 'FORTE';
  } else {
    nivel = 'BOA';
  }

  return {
    municipio: dados.municipio,
    estado: dados.estado,
    categoria: dados.categoria,
    nivel,

    orcamento: {
      total: Math.round(mediaValor),
      executado: dados.anoAtual.executado,
      disponivel: Math.round(disponivel),
      percentualExecutado: Number(percentualExecutado.toFixed(1)),
      percentualDisponivel: Number(percentualDisponivel.toFixed(1))
    },

    contratos: {
      fechados: dados.anoAtual.fechados,
      mediaAnual: Math.round(mediaContratos),
      esperadoAteMes: Math.round(esperadoContratos),
      gap: Math.round(gapContratos),
      gapPercentual: Number(gapPercentual.toFixed(1)),
      projecaoAno: Math.round(projecaoAno)
    },

    oportunidades: {
      editaisAtivos: dados.anoAtual.editaisAtivos.quantidade,
      valorEditais: dados.anoAtual.editaisAtivos.valor,
      orcamentoLivre: Math.round(orcamentoLivre),
      diferencaFinanceira: Math.round(diferencaFinanceira),
      diferencaFinanceiraPercent: Number(diferencaFinanceiraPercent.toFixed(1))
    },

    historico: dados.historico.map(h => ({
      ano: h.ano,
      contratos: h.totalContratos,
      valorExecutado: h.valorExecutado,
      ticketMedio: Math.round(h.valorExecutado / h.totalContratos)
    })),

    comparacao: {
      esperadoContratos: Math.round(esperadoContratos),
      realContratos: dados.anoAtual.fechados,
      esperadoValor: Math.round(esperadoValor),
      realValor: dados.anoAtual.executado
    }
  };
}

// Formatadores de números
export const formatters = {
  currency: (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      notation: 'compact',
      maximumFractionDigits: 2
    }).format(value);
  },

  number: (value: number): string => {
    return new Intl.NumberFormat('pt-BR').format(value);
  },

  percent: (value: number): string => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  }
};
