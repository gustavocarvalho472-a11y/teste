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
  referenceValue: number; // Valor de referência (média/último período)
  referencePeriod: string; // "2020" ou "Média 2016-2020"
  currentValue: number;
  difference: number; // Diferença em R$
  percentageDiff: number; // Diferença em %
  extraAvailable: number; // Dinheiro extra sobrando
  isAnomaly: boolean; // Se está fora do padrão
  severity: 'critical' | 'moderate' | 'normal'; // Severidade da anomalia
}

export interface RankingFilters {
  comparisonMode: ComparisonMode;
  entityType: EntityType | 'all';
  region?: string;
  state?: string;
  minSeverityScore?: number;
  showOnlyAnomalies?: boolean;
}
