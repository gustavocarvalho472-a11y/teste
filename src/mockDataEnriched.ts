import { BudgetData } from './types';

// Gera dados mock enriquecidos com variações realistas incluindo anomalias
export const generateEnrichedMockData = (): BudgetData[] => {
  const data: BudgetData[] = [];
  const startYear = 2015;
  const endYear = 2024;

  // População brasileira com crescimento anual
  const populationByYear: Record<number, number> = {
    2015: 204000000,
    2016: 206000000,
    2017: 208000000,
    2018: 210000000,
    2019: 211000000,
    2020: 213000000,
    2021: 214000000,
    2022: 215000000,
    2023: 216000000,
    2024: 217000000,
  };

  // Base estudantil com declínio demográfico
  const studentsByYear: Record<number, number> = {
    2015: 48500000,
    2016: 48200000,
    2017: 48000000,
    2018: 47800000,
    2019: 47500000,
    2020: 47200000,
    2021: 47000000,
    2022: 46800000,
    2023: 46600000,
    2024: 46400000,
  };

  // Anos eleitorais
  const electionYears = [2016, 2018, 2020, 2022, 2024];

  // Multiplicadores especiais por ano para criar anomalias realistas
  const yearMultipliers: Record<number, number> = {
    2015: 1.0,
    2016: 0.92,  // 🔴 Crise econômica + impeachment
    2017: 0.95,  // Recuperação lenta
    2018: 1.05,  // Ano eleitoral
    2019: 0.77,  // 🔴 ANOMALIA: Corte histórico Bolsonaro
    2020: 0.82,  // 🔴 Pandemia início
    2021: 0.85,  // Pandemia continua
    2022: 1.08,  // 🟡 Ano eleitoral + recuperação
    2023: 1.12,  // 🟡 Novo governo + expansão
    2024: 1.15,  // 🟡 Ano eleitoral + continuidade
  };

  for (let year = startYear; year <= endYear; year++) {
    const isElectionYear = electionYears.includes(year);
    const population = populationByYear[year];
    const students = studentsByYear[year];

    // Orçamento base cresce moderadamente
    const baseAmount = 130000000000 + (year - startYear) * 8000000000;

    // Aplica multiplicador específico do ano
    const yearMultiplier = yearMultipliers[year] || 1.0;

    // Variação eleitoral adicional (anos eleitorais normalmente têm +3-5%)
    const electionBonus = isElectionYear && year !== 2016 && year !== 2020 ? 1.04 : 1.0;

    for (let month = 1; month <= 12; month++) {
      // Variação mensal natural (maior no início do ano fiscal)
      const monthlyVariation = 0.90 + (Math.sin((month - 1) * Math.PI / 6) * 0.10);

      const planned = baseAmount * yearMultiplier * electionBonus * monthlyVariation;

      // Taxa de execução varia por contexto
      let executionRate = 0.80 + Math.random() * 0.15; // Base: 80-95%

      // Anos de crise têm execução menor
      if (year === 2016 || year === 2019 || year === 2020) {
        executionRate *= 0.92;
      }

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

export const enrichedMockData = generateEnrichedMockData();
