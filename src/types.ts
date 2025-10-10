// Interfaces e tipos para o dashboard

export interface BudgetData {
  year: number;
  month: number;
  isElectionYear: boolean;
  planned: number;
  executed: number;
  available: number;
  population: number;
  students: number;
  category: string;
}

export type ComparisonType = 'same-month-last-year' | 'previous-month' | 'electoral-period';
export type ViewFilter = 'electoral' | 'monthly' | 'annual';
export type IndicatorType = 'total-budget' | 'executed' | 'available';
export type AnalysisMode = 'absolute' | 'per-capita' | 'per-student';
export type MonthSelection = 'current' | 'ytd' | 'year';
