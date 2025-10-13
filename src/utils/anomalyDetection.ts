// Utilitários para detecção de anomalias estatísticas

export interface AnomalyData {
  year: number;
  month: number;
  value: number;
  mean: number;
  stdDev: number;
  zScore: number;
  severity: 'critical' | 'moderate' | 'normal';
  percentageDeviation: number;
  context?: string;
  icon?: string;
}

export interface YearlyAnomaly {
  year: number;
  value: number;
  mean: number;
  stdDev: number;
  zScore: number;
  severity: 'critical' | 'moderate' | 'normal';
  percentageDeviation: number;
  isElectionYear: boolean;
  governmentContext: string;
  events: string[];
}

// Calcula média
export const calculateMean = (values: number[]): number => {
  return values.reduce((sum, val) => sum + val, 0) / values.length;
};

// Calcula desvio padrão
export const calculateStdDev = (values: number[], mean: number): number => {
  const squaredDiffs = values.map(val => Math.pow(val - mean, 2));
  const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / values.length;
  return Math.sqrt(variance);
};

// Calcula Z-score (quantos desvios padrão da média)
export const calculateZScore = (value: number, mean: number, stdDev: number): number => {
  if (stdDev === 0) return 0;
  return (value - mean) / stdDev;
};

// Classifica severidade da anomalia
export const classifySeverity = (zScore: number): 'critical' | 'moderate' | 'normal' => {
  const absZScore = Math.abs(zScore);
  if (absZScore > 3) return 'critical';
  if (absZScore > 2) return 'moderate';
  return 'normal';
};

// Obtém cor baseada na severidade
export const getSeverityColor = (severity: 'critical' | 'moderate' | 'normal'): string => {
  switch (severity) {
    case 'critical':
      return '#ef4444';
    case 'moderate':
      return '#f59e0b';
    case 'normal':
      return '#10b981';
  }
};

// Obtém ícone baseado na severidade
export const getSeverityIcon = (severity: 'critical' | 'moderate' | 'normal'): string => {
  switch (severity) {
    case 'critical':
      return '🔴';
    case 'moderate':
      return '🟡';
    case 'normal':
      return '🟢';
  }
};

// Contexto de governo por ano
export const getGovernmentContext = (year: number): string => {
  if (year >= 2023) return 'Governo Lula 3';
  if (year >= 2019) return 'Governo Bolsonaro';
  if (year >= 2016) return 'Governo Temer';
  if (year >= 2011) return 'Governo Dilma';
  if (year >= 2003) return 'Governo Lula 1-2';
  return 'Governo anterior';
};

// Eventos especiais por ano
export const getYearEvents = (year: number): string[] => {
  const events: string[] = [];

  if (year === 2020 || year === 2021) {
    events.push('🦠 Pandemia COVID-19');
  }

  if (year % 4 === 0) {
    events.push('🗳️ Eleição Municipal');
  }

  if (year === 2018 || year === 2022) {
    events.push('🗳️ Eleição Federal');
  }

  if (year === 2019) {
    events.push('👤 Mudança de Governo');
  }

  if (year === 2023) {
    events.push('👤 Mudança de Governo');
  }

  if (year === 2015 || year === 2016) {
    events.push('⚠️ Crise Econômica');
  }

  return events;
};

// Detecta anomalias em série temporal anual
export const detectYearlyAnomalies = (
  yearlyData: { year: number; value: number; isElectionYear: boolean }[]
): YearlyAnomaly[] => {
  const values = yearlyData.map(d => d.value);
  const mean = calculateMean(values);
  const stdDev = calculateStdDev(values, mean);

  return yearlyData.map(data => {
    const zScore = calculateZScore(data.value, mean, stdDev);
    const severity = classifySeverity(zScore);
    const percentageDeviation = ((data.value - mean) / mean) * 100;

    return {
      year: data.year,
      value: data.value,
      mean,
      stdDev,
      zScore,
      severity,
      percentageDeviation,
      isElectionYear: data.isElectionYear,
      governmentContext: getGovernmentContext(data.year),
      events: getYearEvents(data.year)
    };
  });
};

// Identifica as maiores anomalias
export const getTopAnomalies = (
  anomalies: YearlyAnomaly[],
  limit: number = 3
): YearlyAnomaly[] => {
  return [...anomalies]
    .sort((a, b) => Math.abs(b.zScore) - Math.abs(a.zScore))
    .slice(0, limit);
};

// Calcula estatísticas gerais
export const calculateAnomalyStats = (anomalies: YearlyAnomaly[]) => {
  const critical = anomalies.filter(a => a.severity === 'critical').length;
  const moderate = anomalies.filter(a => a.severity === 'moderate').length;
  const total = anomalies.length;

  const electionYears = anomalies.filter(a => a.isElectionYear);
  const nonElectionYears = anomalies.filter(a => !a.isElectionYear);

  const electionAvg = calculateMean(electionYears.map(a => a.value));
  const nonElectionAvg = calculateMean(nonElectionYears.map(a => a.value));
  const electionPattern = ((electionAvg - nonElectionAvg) / nonElectionAvg) * 100;

  return {
    totalAnomalies: critical + moderate,
    criticalCount: critical,
    moderateCount: moderate,
    normalCount: total - critical - moderate,
    electionPattern,
    maxAnomaly: Math.max(...anomalies.map(a => Math.abs(a.zScore))),
    minAnomaly: Math.min(...anomalies.map(a => Math.abs(a.zScore)))
  };
};
