import { MunicipalityBudget, EntityType } from '../types/municipality';

// Lista de municípios brasileiros para simulação
const municipalities = [
  { name: 'São Paulo', state: 'SP', region: 'Sudeste', population: 12300000, students: 2200000 },
  { name: 'Rio de Janeiro', state: 'RJ', region: 'Sudeste', population: 6700000, students: 1100000 },
  { name: 'Brasília', state: 'DF', region: 'Centro-Oeste', population: 3000000, students: 550000 },
  { name: 'Salvador', state: 'BA', region: 'Nordeste', population: 2900000, students: 520000 },
  { name: 'Fortaleza', state: 'CE', region: 'Nordeste', population: 2700000, students: 490000 },
  { name: 'Belo Horizonte', state: 'MG', region: 'Sudeste', population: 2500000, students: 450000 },
  { name: 'Manaus', state: 'AM', region: 'Norte', population: 2200000, students: 420000 },
  { name: 'Curitiba', state: 'PR', region: 'Sul', population: 1900000, students: 350000 },
  { name: 'Recife', state: 'PE', region: 'Nordeste', population: 1600000, students: 310000 },
  { name: 'Porto Alegre', state: 'RS', region: 'Sul', population: 1500000, students: 280000 },
  { name: 'Goiânia', state: 'GO', region: 'Centro-Oeste', population: 1500000, students: 290000 },
  { name: 'Belém', state: 'PA', region: 'Norte', population: 1500000, students: 300000 },
  { name: 'Guarulhos', state: 'SP', region: 'Sudeste', population: 1400000, students: 270000 },
  { name: 'Campinas', state: 'SP', region: 'Sudeste', population: 1200000, students: 230000 },
  { name: 'São Luís', state: 'MA', region: 'Nordeste', population: 1100000, students: 240000 },
  { name: 'São Gonçalo', state: 'RJ', region: 'Sudeste', population: 1000000, students: 200000 },
  { name: 'Maceió', state: 'AL', region: 'Nordeste', population: 1000000, students: 210000 },
  { name: 'Duque de Caxias', state: 'RJ', region: 'Sudeste', population: 920000, students: 180000 },
  { name: 'Natal', state: 'RN', region: 'Nordeste', population: 890000, students: 170000 },
  { name: 'Teresina', state: 'PI', region: 'Nordeste', population: 860000, students: 180000 }
];

// Governos por período
const getGovernment = (year: number): string => {
  if (year >= 2023) return 'Lula 3';
  if (year >= 2019) return 'Bolsonaro';
  if (year >= 2016) return 'Temer';
  return 'Dilma';
};

// Eventos por ano
const getEvents = (year: number): string[] => {
  const events: string[] = [];
  if (year === 2020 || year === 2021) events.push('🦠 Pandemia');
  if (year % 4 === 0) events.push('🗳️ Eleição Municipal');
  if (year === 2018 || year === 2022) events.push('🗳️ Eleição Federal');
  return events;
};

// Gera dados mock para um município
const generateMunicipalityData = (
  municipality: typeof municipalities[0],
  index: number
): MunicipalityBudget => {
  const years = [2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024];
  const currentYear = 2024;

  // Budget base varia por tamanho da cidade
  const baseBudget = (municipality.population / 1000000) * 1500000000;

  // Multipliers específicos para criar anomalias realistas
  const yearMultipliers: Record<number, number> = {
    2016: 1.0,
    2018: 0.92,
    2019: 1.05,
    2020: 0.75, // Pandemia - grande corte
    2021: 0.80, // Pandemia continua
    2022: 1.10, // Recuperação + eleição
    2023: 1.08,
    2024: 0.65 // ANOMALIA: Subexecução severa em ano eleitoral
  };

  // Alguns municípios têm comportamento diferente (para criar ranking diverso)
  const municipalityVariation = index % 5;
  let customMultiplier = 1.0;

  if (municipalityVariation === 0) {
    // Subexecução severa em 2024
    yearMultipliers[2024] = 0.42;
  } else if (municipalityVariation === 1) {
    // Subexecução moderada em 2024
    yearMultipliers[2024] = 0.58;
  } else if (municipalityVariation === 2) {
    // Comportamento normal
    yearMultipliers[2024] = 0.85;
  } else if (municipalityVariation === 3) {
    // Execução acima da média (não prioritário)
    yearMultipliers[2024] = 0.95;
  } else {
    // Subexecução crítica
    yearMultipliers[2024] = 0.38;
  }

  // Gera histórico
  const history = years.map(year => {
    const yearBudget = baseBudget * (1 + (year - 2016) * 0.05);
    const multiplier = yearMultipliers[year] || 1.0;
    const executed = yearBudget * multiplier;
    const available = yearBudget - executed;

    return {
      year,
      totalBudget: yearBudget,
      executed,
      available,
      executionRate: (executed / yearBudget) * 100,
      isElectionYear: year % 4 === 0 || year === 2018 || year === 2022
    };
  });

  // Dados do ano atual
  const current = history.find(h => h.year === currentYear)!;

  // Calcula comparações
  const electoralYears = history.filter(h => h.isElectionYear && h.year < currentYear);
  const avgElectoralExecution = electoralYears.reduce((sum, h) => sum + h.executionRate, 0) / electoralYears.length;
  const avgElectoralValue = electoralYears.reduce((sum, h) => sum + h.executed, 0) / electoralYears.length;

  const lastElectoral = electoralYears[electoralYears.length - 1];

  const allYears = history.filter(h => h.year < currentYear);
  const avgAllExecution = allYears.reduce((sum, h) => sum + h.executionRate, 0) / allYears.length;
  const avgAllValue = allYears.reduce((sum, h) => sum + h.executed, 0) / allYears.length;

  const previousYear = history.find(h => h.year === currentYear - 1)!;

  // Calcula métricas de comparação
  const calculateComparison = (referenceValue: number, referencePeriod: string) => {
    const difference = current.executed - referenceValue;
    const percentageDiff = (difference / referenceValue) * 100;

    // Dinheiro extra sobrando (valor negativo de difference significa menos gasto)
    const referenceAvailable = current.totalBudget - referenceValue;
    const extraAvailable = current.available - referenceAvailable;

    const isAnomaly = Math.abs(percentageDiff) > 15;
    const severity: 'critical' | 'moderate' | 'normal' =
      Math.abs(percentageDiff) > 30 ? 'critical' :
      Math.abs(percentageDiff) > 15 ? 'moderate' : 'normal';

    return {
      referenceValue,
      referencePeriod,
      currentValue: current.executed,
      difference,
      percentageDiff,
      extraAvailable,
      isAnomaly,
      severity
    };
  };

  // Calcula severity score (prioriza quem tem mais dinheiro sobrando vs média)
  const avgElectoralComparison = calculateComparison(avgElectoralValue, 'Média Eleitorais');
  const severityScore = Math.min(100, Math.max(0,
    (Math.abs(avgElectoralComparison.percentageDiff) * 2) +
    (avgElectoralComparison.extraAvailable > 0 ? 20 : 0)
  ));

  return {
    id: `mun-${index}`,
    name: municipality.name,
    state: municipality.state,
    region: municipality.region,
    type: 'municipality',
    currentYear,
    totalBudget: current.totalBudget,
    executed: current.executed,
    available: current.available,
    executionRate: current.executionRate,
    history,
    comparison: {
      avgElectoral: calculateComparison(avgElectoralValue, `Média ${electoralYears[0].year}-${electoralYears[electoralYears.length - 1].year}`),
      lastElectoral: calculateComparison(lastElectoral.executed, lastElectoral.year.toString()),
      avgAll: calculateComparison(avgAllValue, 'Média Geral'),
      previousYear: calculateComparison(previousYear.executed, previousYear.year.toString())
    },
    isElectionYear: currentYear % 4 === 0,
    government: getGovernment(currentYear),
    events: getEvents(currentYear),
    population: municipality.population,
    students: municipality.students,
    severityScore
  };
};

// Gera todos os dados
export const municipalityBudgetData: MunicipalityBudget[] = municipalities.map(generateMunicipalityData);
