import { BudgetData } from './types';

// Gera dados mock realistas para 5 anos (2020-2024)
export const generateMockData = (): BudgetData[] => {
  const data: BudgetData[] = [];
  const startYear = 2020;
  const endYear = 2024;

  // População brasileira com crescimento anual
  const populationByYear: Record<number, number> = {
    2020: 213000000,
    2021: 214000000,
    2022: 215000000,
    2023: 216000000,
    2024: 217000000,
  };

  // Base estudantil com declínio demográfico
  const studentsByYear: Record<number, number> = {
    2020: 47200000,
    2021: 47000000,
    2022: 46800000,
    2023: 46600000,
    2024: 46400000,
  };

  // Anos eleitorais
  const electionYears = [2020, 2022, 2024];

  for (let year = startYear; year <= endYear; year++) {
    const isElectionYear = electionYears.includes(year);
    const population = populationByYear[year];
    const students = studentsByYear[year];

    // Orçamento base cresce a cada ano
    const baseAmount = 150000000000 + (year - startYear) * 12000000000;

    // Anos eleitorais têm aumento de ~8%
    const yearMultiplier = isElectionYear ? 1.08 : 1.0;

    for (let month = 1; month <= 12; month++) {
      // Variação mensal natural (maior no início do ano)
      const monthlyVariation = 0.85 + (Math.sin((month - 1) * Math.PI / 6) * 0.15);

      const planned = baseAmount * yearMultiplier * monthlyVariation;
      const executionRate = 0.75 + Math.random() * 0.2; // 75-95% de execução
      const executed = planned * executionRate;
      const available = planned - executed;

      data.push({
        year,
        month,
        isElectionYear,
        planned,
        executed,
        available,
        population,
        students,
        category: 'Educação'
      });
    }
  }

  return data;
};

export const mockData = generateMockData();
