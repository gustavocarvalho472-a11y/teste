// Centralização de todos os textos do sistema
// Para facilitar manutenção e tradução futura

export const COPY = {
  // ========== HEADER PRINCIPAL ==========
  header: {
    eyebrow: "INTELIGÊNCIA ORÇAMENTÁRIA · 5.570 MUNICÍPIOS MONITORADOS · AGOSTO/2025",
    title: "Onde está sobrando orçamento público?",
    subtitle: "Identificamos 836 municípios (15%) que executaram menos que o esperado até agosto/2025 comparado à média 2022-2024. Isso representa R$ 36 milhões em orçamento disponível acima do padrão histórico.",
    context: "Estamos em agosto (mês 8/12). Comparando com a média dos últimos 3 anos (2022-2024), o esperado é que 67% do orçamento anual já esteja executado. Municípios que executaram <70% apresentam oportunidade comercial significativa.",
    comparisonPeriod: "Média 2022-2024"
  },

  // ========== SIMULAÇÃO REALISTA (AGOSTO/2025) ==========
  simulation: {
    // Contexto Temporal
    currentMonth: "Agosto",
    currentMonthNumber: 8,
    currentYear: 2025,
    totalMonths: 12,
    comparisonPeriod: "Média 2022-2024",
    comparisonYears: "2022, 2023 e 2024",

    // Contexto Geral
    totalMunicipalities: 5570,

    // Municípios com Desvio
    withDeviation: 836, // 15% dos municípios com desvio significativo
    percentWithDeviation: 15.0, // 15.0% do total

    // Breakdown por Nível
    highOpportunity: 180, // >15% abaixo do esperado (3% do total)
    mediumOpportunity: 320, // 8-15% abaixo (6% do total)
    lowOpportunity: 336, // 3-8% abaixo (6% do total)

    // Orçamento Total (todos os municípios)
    budgetTotal: 245e9, // R$ 245 bilhões anuais
    executedTotal: 171.5e9, // R$ 171.5 bilhões executados até agosto (70% do total)
    availableTotal: 78e9, // R$ 78 bilhões disponíveis restantes

    // Orçamento nos 836 municípios com desvio
    budgetDeviation: 71e9, // R$ 71 bi de orçamento anual nos 836 municípios
    executedDeviation: 49.7e9, // R$ 49.7 bi executados (70% - abaixo da média)
    availableDeviation: 21.3e9, // R$ 21.3 bi disponíveis nos 836

    // Oportunidade Comercial (sobra acima do padrão)
    opportunityValue: 36e6, // R$ 36 milhões acima da média histórica (2022-2024)

    // Taxas de Execução
    expectedExecutionRate: 67, // 67% esperado até agosto (média 2022-2024)
    actualExecutionRateDeviation: 70, // 70% real nos 836 municípios
    historicalExecutionRate: 85, // 85% ao final do ano (média histórica)
    deviationPoints: 3 // +3 pontos percentuais de diferença
  },

  // ========== CARDS DE MÉTRICAS PRINCIPAIS ==========
  metrics: {
    totalDisponivel: {
      icon: "attach_money",
      label: "RECURSOS DISPONÍVEIS AGORA",
      labelSecondary: "(Sobrou de {total} alocados)",
      extra: "+{valor} acima da média histórica"
    },
    taxaExecucao: {
      icon: "bar_chart",
      label: "QUANTO FOI GASTO ATÉ AGORA",
      labelSecondary: "({executado} dos {total})",
      context: "Média histórica: {media}% neste período",
      alert: "↓ Estão gastando menos que o normal"
    },
    desvio: {
      icon: "gps_fixed",
      label: "MUNICÍPIOS FORA DO PADRÃO",
      count: "{count} municípios",
      description: "Gastando significativamente menos que a média",
      percentage: "↓ {percent}% abaixo do padrão de execução"
    },
    municipiosAnalisados: {
      icon: "search",
      label: "TOP OPORTUNIDADES",
      count: "{count} municípios",
      description: "Com mais recursos sobrando",
      context: "Dos {total} fora do padrão identificados"
    }
  },

  // ========== BADGES DE OPORTUNIDADE ==========
  badges: {
    ALTA: {
      label: "OPORTUNIDADE ALTA",
      icon: "▲",
      description: "+50% acima da média",
      threshold: 50
    },
    MEDIA: {
      label: "OPORTUNIDADE MÉDIA",
      icon: "●",
      description: "+20% a +49%",
      threshold: 20
    },
    BAIXA: {
      label: "OPORTUNIDADE BAIXA",
      icon: "○",
      description: "+5% a +19%",
      threshold: 5
    }
  },

  // ========== SEÇÕES ==========
  sections: {
    topEstados: {
      icon: "▼",
      title: "Estados com Mais Recursos Disponíveis",
      subtitle: "Onde está concentrado o maior volume de dinheiro sobrando",
      itemExtra: "+{valor} acima da média histórica"
    },
    prioritarios: {
      icon: "location_city",
      title: "Municípios Prioritários",
      subtitle: "Selecionados por volume de oportunidade (>R$ 50 mi) e desvio crítico (>-20%) vs média 2022-2024",
      showing: "Mostrando {count} municípios",
      totalOpportunity: "Total de oportunidade: {value}",
      viewAll: "Ver todos os {total} municípios prioritários",
      criteria: {
        minSobra: 50000000, // R$ 50 milhões
        minDesvio: -20, // -20%
        minOrcamento: 200000000 // R$ 200 milhões
      }
    },
    grafico: {
      icon: "■",
      title: "Ranking de Oportunidades",
      subtitle: "Quanto cada município tem disponível vs o que normalmente tem",
      tabs: {
        extra: "Dinheiro Sobrando",
        executed: "Quanto Gastaram",
        deviation: "Diferença do Padrão"
      }
    },
    lista: {
      icon: "▪",
      title: "Municípios ({count})",
      pagination: "Página {current} de {total}"
    }
  },

  // ========== CARDS TOP 3 ==========
  top3Card: {
    disponivel: {
      title: "💰 Quanto está disponível agora",
      value: "{valor} sobrando ({percent}% não foi gasto)"
    },
    sobrou: {
      title: "📊 Quanto SOBROU A MAIS que o normal",
      value: "+{valor} acima da média dos últimos períodos",
      comparison: "Normalmente sobrava: {normal}\nAgora está sobrando: {atual}"
    },
    porqueOportunidade: {
      title: "💡 Por que é oportunidade?",
      ALTA: "Está gastando muito menos que o histórico ({atual}% vs {historico}% normalmente). Há {valor} A MAIS disponível para negócios estratégicos.",
      MEDIA: "Recursos disponíveis {percent}% acima da média. Vale avaliar timing para abordagem comercial.",
      BAIXA: "Disponibilidade ligeiramente acima do histórico. Monitorar evolução antes de ação comercial."
    },
    ctas: {
      verAnalise: "📊 Ver Análise Completa",
      exportar: "📥 Exportar Relatório"
    }
  },

  // ========== CARDS DE LISTA ==========
  listaCard: {
    disponivel: "+{valor} a mais que o normal",
    gastaram: "Gastaram: {executado} de {total} ({percent}%)",
    mediaHistorica: "Média histórica: {media}% gasto neste período",
    porqueOlhar: "🎯 Por que olhar agora?\n+{percent}% mais recursos disponíveis vs média dos últimos períodos eleitorais",
    ctas: {
      verDetalhes: "Ver Detalhes",
      adicionar: "Adicionar à Lista"
    }
  },

  // ========== FILTROS ==========
  filters: {
    titulo: "📊 COMO COMPARAR OS DADOS",
    subtitulo: "Escolha com qual período você quer comparar para encontrar oportunidades:",
    modes: {
      avgElectoral: "🗳️ Média Períodos Eleitorais",
      lastElectoral: "🗳️ Último Período Eleitoral (2020)",
      avgAll: "📅 Média de Todos os Anos",
      previousYear: "📅 Ano Passado (2023)"
    },
    recomendacao: "💡 Recomendamos \"Média Períodos Eleitorais\" para identificar padrões consistentes de subexecução.",
    ordenar: {
      label: "Ordenar resultados por:",
      options: {
        extra: "💰 Maior Disponibilidade",
        deviation: "📈 Maior Diferença do Padrão",
        opportunity: "🎯 Nível de Oportunidade"
      }
    },
    analisando: "Analisando: {current} (Atual)",
    comparando: "Comparando com: {comparison}"
  },

  // ========== TOOLTIPS ==========
  tooltips: {
    executado: "Quanto do orçamento já foi gasto até agora.\nExemplo: 72% = gastaram R$ 7,20 de cada R$ 10 disponíveis",
    disponivel: "Quanto de dinheiro ainda não foi comprometido/gasto.\nÉ este valor que representa a oportunidade de negócio.",
    desvio: "Quanto o comportamento atual está diferente do histórico.\n↓ Negativo = Gastando menos que o normal (OPORTUNIDADE)\n↑ Positivo = Gastando mais que o normal",
    mediaEleitoral: "Comparamos 2024 com a média de 2016 e 2020.\nAnos eleitorais tendem a ter padrões de gasto similares,\ntornando a comparação mais relevante."
  },

  // ========== MENSAGENS DE ESTADO ==========
  empty: {
    title: "🔍 Nenhuma oportunidade encontrada com estes filtros",
    suggestions: "Tente:\n- Ajustar o período de comparação\n- Reduzir os filtros aplicados\n- Ordenar por \"Maior Diferença do Padrão\"",
    cta: "Limpar Filtros",
    context: "para ver todas as {total} oportunidades identificadas."
  },

  // ========== FOOTER ==========
  footer: {
    text: "Painel Estratégico de Gestão Orçamentária · Visão Consolidada Nacional"
  }
};

// ========== FUNÇÕES AUXILIARES ==========

export function getBadgeByDeviation(deviation: number): keyof typeof COPY.badges {
  const absDeviation = Math.abs(deviation);
  if (absDeviation >= 50) return 'ALTA';
  if (absDeviation >= 20) return 'MEDIA';
  return 'BAIXA';
}

export function formatCopyTemplate(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key) => String(vars[key] ?? match));
}

export function getOpportunityExplanation(
  level: keyof typeof COPY.badges,
  currentPercent: number,
  historicalPercent: number,
  extraValue: number
): string {
  const template = COPY.top3Card.porqueOportunidade[level];
  return formatCopyTemplate(template, {
    atual: currentPercent.toFixed(1),
    historico: historicalPercent.toFixed(1),
    valor: `R$ ${(extraValue / 1e9).toFixed(1)} BI`,
    percent: Math.abs(((currentPercent - historicalPercent) / historicalPercent) * 100).toFixed(0)
  });
}
