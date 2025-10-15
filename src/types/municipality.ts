// Tipos para análise municipal de subexecução orçamentária

export type ComparisonMode =
  | 'avg-electoral' // Média dos períodos eleitorais
  | 'last-electoral' // Último período eleitoral
  | 'avg-all' // Média geral todos os anos
  | 'previous-year'; // Ano anterior

export type EntityType = 'municipality' | 'state' | 'region' | 'federal';

export interface MunicipalityBudget {
  id: string;
  name: string;
  state: string;
  region: string;
  type: EntityType;

  // Orçamento atual
  currentYear: number;
  totalBudget: number;
  executed: number;
  available: number;
  executionRate: number; // Percentual executado (0-100)

  // Histórico por ano
  history: YearlyBudget[];

  // Comparações calculadas
  comparison: {
    avgElectoral: ComparisonMetrics;
    lastElectoral: ComparisonMetrics;
    avgAll: ComparisonMetrics;
    previousYear: ComparisonMetrics;
  };

  // Contexto
  isElectionYear: boolean;
  government: string;
  events: string[];
  population: number;
  students: number;

  // Score de prioridade (0-100, quanto maior mais prioritário)
  severityScore: number;
}

export interface YearlyBudget {
  year: number;
  totalBudget: number;
  executed: number;
  available: number;
  executionRate: number;
  isElectionYear: boolean;
}

export interface ComparisonMetrics {
  // Nova estrutura
  executedAmount: number; // Valor executado atual
  referenceAmount: number; // Valor de referência para comparação
  percentageDeviation: number; // Desvio percentual (negativo = subexecução)
  severity: 'critical' | 'high' | 'moderate' | 'normal'; // Severidade

  // Propriedades legadas (para compatibilidade)
  referenceValue?: number;
  referencePeriod?: string;
  currentValue?: number;
  difference?: number;
  percentageDiff?: number;
  extraAvailable?: number;
  isAnomaly?: boolean;
}

export interface RankingFilters {
  comparisonMode: ComparisonMode;
  entityType: EntityType | 'all';
  region?: string;
  state?: string;
  minSeverityScore?: number;
  showOnlyAnomalies?: boolean;
}
