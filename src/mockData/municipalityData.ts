import { MunicipalityBudget, EntityType } from '../types/municipality';

// Lista expandida de 100 municípios brasileiros
const municipalities = [
  // Capitais e grandes cidades
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

  // Cidades médias e grandes do interior
  { name: 'Goiânia', state: 'GO', region: 'Centro-Oeste', population: 1500000, students: 290000 },
  { name: 'Belém', state: 'PA', region: 'Norte', population: 1500000, students: 300000 },
  { name: 'Guarulhos', state: 'SP', region: 'Sudeste', population: 1400000, students: 270000 },
  { name: 'Campinas', state: 'SP', region: 'Sudeste', population: 1200000, students: 230000 },
  { name: 'São Luís', state: 'MA', region: 'Nordeste', population: 1100000, students: 240000 },
  { name: 'São Gonçalo', state: 'RJ', region: 'Sudeste', population: 1000000, students: 200000 },
  { name: 'Maceió', state: 'AL', region: 'Nordeste', population: 1000000, students: 210000 },
  { name: 'Duque de Caxias', state: 'RJ', region: 'Sudeste', population: 920000, students: 180000 },
  { name: 'Natal', state: 'RN', region: 'Nordeste', population: 890000, students: 170000 },
  { name: 'Teresina', state: 'PI', region: 'Nordeste', population: 860000, students: 180000 },

  { name: 'Campo Grande', state: 'MS', region: 'Centro-Oeste', population: 900000, students: 175000 },
  { name: 'João Pessoa', state: 'PB', region: 'Nordeste', population: 820000, students: 160000 },
  { name: 'Jaboatão', state: 'PE', region: 'Nordeste', population: 710000, students: 145000 },
  { name: 'Santo André', state: 'SP', region: 'Sudeste', population: 720000, students: 140000 },
  { name: 'Osasco', state: 'SP', region: 'Sudeste', population: 700000, students: 138000 },
  { name: 'São Bernardo', state: 'SP', region: 'Sudeste', population: 840000, students: 165000 },
  { name: 'Uberlândia', state: 'MG', region: 'Sudeste', population: 690000, students: 135000 },
  { name: 'Contagem', state: 'MG', region: 'Sudeste', population: 670000, students: 132000 },
  { name: 'Sorocaba', state: 'SP', region: 'Sudeste', population: 680000, students: 133000 },
  { name: 'Aracaju', state: 'SE', region: 'Nordeste', population: 660000, students: 130000 },

  { name: 'Feira de Santana', state: 'BA', region: 'Nordeste', population: 620000, students: 125000 },
  { name: 'Joinville', state: 'SC', region: 'Sul', population: 590000, students: 118000 },
  { name: 'Juiz de Fora', state: 'MG', region: 'Sudeste', population: 570000, students: 115000 },
  { name: 'Londrina', state: 'PR', region: 'Sul', population: 580000, students: 117000 },
  { name: 'Aparecida de Goiânia', state: 'GO', region: 'Centro-Oeste', population: 540000, students: 110000 },
  { name: 'Niterói', state: 'RJ', region: 'Sudeste', population: 510000, students: 105000 },
  { name: 'Belford Roxo', state: 'RJ', region: 'Sudeste', population: 510000, students: 102000 },
  { name: 'Caxias do Sul', state: 'RS', region: 'Sul', population: 520000, students: 106000 },
  { name: 'Campos dos Goytacazes', state: 'RJ', region: 'Sudeste', population: 510000, students: 103000 },
  { name: 'Macapá', state: 'AP', region: 'Norte', population: 500000, students: 105000 },

  { name: 'São José dos Campos', state: 'SP', region: 'Sudeste', population: 730000, students: 145000 },
  { name: 'Ribeirão Preto', state: 'SP', region: 'Sudeste', population: 710000, students: 143000 },
  { name: 'Santos', state: 'SP', region: 'Sudeste', population: 430000, students: 88000 },
  { name: 'Mauá', state: 'SP', region: 'Sudeste', population: 470000, students: 96000 },
  { name: 'São José do Rio Preto', state: 'SP', region: 'Sudeste', population: 460000, students: 94000 },
  { name: 'Mogi das Cruzes', state: 'SP', region: 'Sudeste', population: 450000, students: 92000 },
  { name: 'Diadema', state: 'SP', region: 'Sudeste', population: 420000, students: 86000 },
  { name: 'Piracicaba', state: 'SP', region: 'Sudeste', population: 410000, students: 84000 },
  { name: 'Carapicuíba', state: 'SP', region: 'Sudeste', population: 400000, students: 82000 },
  { name: 'Bauru', state: 'SP', region: 'Sudeste', population: 380000, students: 78000 },

  { name: 'Montes Claros', state: 'MG', region: 'Sudeste', population: 410000, students: 85000 },
  { name: 'Vitória', state: 'ES', region: 'Sudeste', population: 370000, students: 76000 },
  { name: 'Vila Velha', state: 'ES', region: 'Sudeste', population: 500000, students: 102000 },
  { name: 'Serra', state: 'ES', region: 'Sudeste', population: 520000, students: 106000 },
  { name: 'Cariacica', state: 'ES', region: 'Sudeste', population: 380000, students: 78000 },
  { name: 'Vitória da Conquista', state: 'BA', region: 'Nordeste', population: 340000, students: 71000 },
  { name: 'Caruaru', state: 'PE', region: 'Nordeste', population: 360000, students: 74000 },
  { name: 'Petrolina', state: 'PE', region: 'Nordeste', population: 350000, students: 73000 },
  { name: 'Caucaia', state: 'CE', region: 'Nordeste', population: 370000, students: 77000 },
  { name: 'Juazeiro do Norte', state: 'CE', region: 'Nordeste', population: 280000, students: 59000 },

  { name: 'Maringá', state: 'PR', region: 'Sul', population: 430000, students: 89000 },
  { name: 'Ponta Grossa', state: 'PR', region: 'Sul', population: 360000, students: 75000 },
  { name: 'Cascavel', state: 'PR', region: 'Sul', population: 330000, students: 69000 },
  { name: 'Foz do Iguaçu', state: 'PR', region: 'Sul', population: 260000, students: 55000 },
  { name: 'Pelotas', state: 'RS', region: 'Sul', population: 340000, students: 71000 },
  { name: 'Canoas', state: 'RS', region: 'Sul', population: 350000, students: 72000 },
  { name: 'Santa Maria', state: 'RS', region: 'Sul', population: 280000, students: 59000 },
  { name: 'Gravataí', state: 'RS', region: 'Sul', population: 280000, students: 58000 },
  { name: 'Viamão', state: 'RS', region: 'Sul', population: 260000, students: 55000 },
  { name: 'Novo Hamburgo', state: 'RS', region: 'Sul', population: 250000, students: 52000 },

  { name: 'Blumenau', state: 'SC', region: 'Sul', population: 360000, students: 75000 },
  { name: 'São José', state: 'SC', region: 'Sul', population: 250000, students: 53000 },
  { name: 'Chapecó', state: 'SC', region: 'Sul', population: 220000, students: 47000 },
  { name: 'Florianópolis', state: 'SC', region: 'Sul', population: 510000, students: 105000 },
  { name: 'Itajaí', state: 'SC', region: 'Sul', population: 220000, students: 46000 },
  { name: 'Criciúma', state: 'SC', region: 'Sul', population: 210000, students: 45000 },
  { name: 'Jaraguá do Sul', state: 'SC', region: 'Sul', population: 180000, students: 39000 },
  { name: 'Lages', state: 'SC', region: 'Sul', population: 160000, students: 35000 },
  { name: 'Palmas', state: 'TO', region: 'Norte', population: 310000, students: 65000 },
  { name: 'Porto Velho', state: 'RO', region: 'Norte', population: 540000, students: 112000 },

  { name: 'Rio Branco', state: 'AC', region: 'Norte', population: 410000, students: 86000 },
  { name: 'Boa Vista', state: 'RR', region: 'Norte', population: 420000, students: 88000 },
  { name: 'Santarém', state: 'PA', region: 'Norte', population: 310000, students: 66000 },
  { name: 'Macapá', state: 'AP', region: 'Norte', population: 520000, students: 108000 },
  { name: 'Ananindeua', state: 'PA', region: 'Norte', population: 530000, students: 110000 },
  { name: 'Cuiabá', state: 'MT', region: 'Centro-Oeste', population: 620000, students: 128000 },
  { name: 'Várzea Grande', state: 'MT', region: 'Centro-Oeste', population: 290000, students: 61000 },
  { name: 'Rondonópolis', state: 'MT', region: 'Centro-Oeste', population: 240000, students: 51000 },
  { name: 'Anápolis', state: 'GO', region: 'Centro-Oeste', population: 390000, students: 82000 },
  { name: 'Imperatriz', state: 'MA', region: 'Nordeste', population: 260000, students: 55000 },

  { name: 'Mossoró', state: 'RN', region: 'Nordeste', population: 300000, students: 63000 },
  { name: 'Parnamirim', state: 'RN', region: 'Nordeste', population: 260000, students: 55000 },
  { name: 'Campina Grande', state: 'PB', region: 'Nordeste', population: 410000, students: 86000 },
  { name: 'Olinda', state: 'PE', region: 'Nordeste', population: 390000, students: 82000 },
  { name: 'Paulista', state: 'PE', region: 'Nordeste', population: 330000, students: 69000 },
  { name: 'Arapiraca', state: 'AL', region: 'Nordeste', population: 240000, students: 51000 },
  { name: 'Ilhéus', state: 'BA', region: 'Nordeste', population: 165000, students: 36000 },
  { name: 'Lauro de Freitas', state: 'BA', region: 'Nordeste', population: 200000, students: 43000 },
  { name: 'Camaçari', state: 'BA', region: 'Nordeste', population: 300000, students: 63000 },

  // Municípios adicionais para simular os 850 com desvio
  // São Paulo (estado com mais municípios) - 180 municípios
  ...Array.from({ length: 180 }, (_, i) => ({
    name: `Município SP ${i + 1}`,
    state: 'SP',
    region: 'Sudeste' as const,
    population: Math.floor(Math.random() * 200000) + 50000,
    students: Math.floor(Math.random() * 40000) + 10000
  })),

  // Minas Gerais - 120 municípios
  ...Array.from({ length: 120 }, (_, i) => ({
    name: `Município MG ${i + 1}`,
    state: 'MG',
    region: 'Sudeste' as const,
    population: Math.floor(Math.random() * 150000) + 40000,
    students: Math.floor(Math.random() * 30000) + 8000
  })),

  // Bahia - 95 municípios
  ...Array.from({ length: 95 }, (_, i) => ({
    name: `Município BA ${i + 1}`,
    state: 'BA',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 180000) + 45000,
    students: Math.floor(Math.random() * 35000) + 9000
  })),

  // Rio Grande do Sul - 70 municípios
  ...Array.from({ length: 70 }, (_, i) => ({
    name: `Município RS ${i + 1}`,
    state: 'RS',
    region: 'Sul' as const,
    population: Math.floor(Math.random() * 120000) + 35000,
    students: Math.floor(Math.random() * 25000) + 7000
  })),

  // Paraná - 65 municípios
  ...Array.from({ length: 65 }, (_, i) => ({
    name: `Município PR ${i + 1}`,
    state: 'PR',
    region: 'Sul' as const,
    population: Math.floor(Math.random() * 130000) + 40000,
    students: Math.floor(Math.random() * 28000) + 8000
  })),

  // Goiás - 50 municípios
  ...Array.from({ length: 50 }, (_, i) => ({
    name: `Município GO ${i + 1}`,
    state: 'GO',
    region: 'Centro-Oeste' as const,
    population: Math.floor(Math.random() * 100000) + 30000,
    students: Math.floor(Math.random() * 22000) + 6000
  })),

  // Ceará - 48 municípios
  ...Array.from({ length: 48 }, (_, i) => ({
    name: `Município CE ${i + 1}`,
    state: 'CE',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 110000) + 35000,
    students: Math.floor(Math.random() * 24000) + 7000
  })),

  // Pernambuco - 40 municípios
  ...Array.from({ length: 40 }, (_, i) => ({
    name: `Município PE ${i + 1}`,
    state: 'PE',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 105000) + 32000,
    students: Math.floor(Math.random() * 23000) + 6500
  })),

  // Santa Catarina - 38 municípios
  ...Array.from({ length: 38 }, (_, i) => ({
    name: `Município SC ${i + 1}`,
    state: 'SC',
    region: 'Sul' as const,
    population: Math.floor(Math.random() * 95000) + 28000,
    students: Math.floor(Math.random() * 20000) + 5500
  })),

  // Pará - 35 municípios
  ...Array.from({ length: 35 }, (_, i) => ({
    name: `Município PA ${i + 1}`,
    state: 'PA',
    region: 'Norte' as const,
    population: Math.floor(Math.random() * 125000) + 38000,
    students: Math.floor(Math.random() * 27000) + 7500
  })),

  // Maranhão - 32 municípios
  ...Array.from({ length: 32 }, (_, i) => ({
    name: `Município MA ${i + 1}`,
    state: 'MA',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 98000) + 30000,
    students: Math.floor(Math.random() * 21000) + 6000
  })),

  // Rio de Janeiro - 28 municípios
  ...Array.from({ length: 28 }, (_, i) => ({
    name: `Município RJ ${i + 1}`,
    state: 'RJ',
    region: 'Sudeste' as const,
    population: Math.floor(Math.random() * 140000) + 42000,
    students: Math.floor(Math.random() * 30000) + 8500
  })),

  // Mato Grosso - 25 municípios
  ...Array.from({ length: 25 }, (_, i) => ({
    name: `Município MT ${i + 1}`,
    state: 'MT',
    region: 'Centro-Oeste' as const,
    population: Math.floor(Math.random() * 85000) + 25000,
    students: Math.floor(Math.random() * 18000) + 5000
  })),

  // Paraíba - 22 municípios
  ...Array.from({ length: 22 }, (_, i) => ({
    name: `Município PB ${i + 1}`,
    state: 'PB',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 92000) + 28000,
    students: Math.floor(Math.random() * 20000) + 5500
  })),

  // Espírito Santo - 18 municípios
  ...Array.from({ length: 18 }, (_, i) => ({
    name: `Município ES ${i + 1}`,
    state: 'ES',
    region: 'Sudeste' as const,
    population: Math.floor(Math.random() * 88000) + 27000,
    students: Math.floor(Math.random() * 19000) + 5300
  })),

  // Piauí - 15 municípios
  ...Array.from({ length: 15 }, (_, i) => ({
    name: `Município PI ${i + 1}`,
    state: 'PI',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 82000) + 25000,
    students: Math.floor(Math.random() * 18000) + 5000
  })),

  // Alagoas - 12 municípios
  ...Array.from({ length: 12 }, (_, i) => ({
    name: `Município AL ${i + 1}`,
    state: 'AL',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 78000) + 24000,
    students: Math.floor(Math.random() * 17000) + 4800
  })),

  // Rio Grande do Norte - 10 municípios
  ...Array.from({ length: 10 }, (_, i) => ({
    name: `Município RN ${i + 1}`,
    state: 'RN',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 75000) + 23000,
    students: Math.floor(Math.random() * 16000) + 4500
  })),

  // Mato Grosso do Sul - 8 municípios
  ...Array.from({ length: 8 }, (_, i) => ({
    name: `Município MS ${i + 1}`,
    state: 'MS',
    region: 'Centro-Oeste' as const,
    population: Math.floor(Math.random() * 72000) + 22000,
    students: Math.floor(Math.random() * 15000) + 4300
  })),

  // Sergipe - 6 municípios
  ...Array.from({ length: 6 }, (_, i) => ({
    name: `Município SE ${i + 1}`,
    state: 'SE',
    region: 'Nordeste' as const,
    population: Math.floor(Math.random() * 68000) + 21000,
    students: Math.floor(Math.random() * 14000) + 4100
  })),

  // Tocantins - 5 municípios
  ...Array.from({ length: 5 }, (_, i) => ({
    name: `Município TO ${i + 1}`,
    state: 'TO',
    region: 'Norte' as const,
    population: Math.floor(Math.random() * 65000) + 20000,
    students: Math.floor(Math.random() * 13500) + 3900
  })),

  // Rondônia - 4 municípios
  ...Array.from({ length: 4 }, (_, i) => ({
    name: `Município RO ${i + 1}`,
    state: 'RO',
    region: 'Norte' as const,
    population: Math.floor(Math.random() * 62000) + 19000,
    students: Math.floor(Math.random() * 13000) + 3700
  })),

  // Amazonas - 3 municípios
  ...Array.from({ length: 3 }, (_, i) => ({
    name: `Município AM ${i + 1}`,
    state: 'AM',
    region: 'Norte' as const,
    population: Math.floor(Math.random() * 68000) + 21000,
    students: Math.floor(Math.random() * 14000) + 4100
  })),

  // Acre - 2 municípios
  ...Array.from({ length: 2 }, (_, i) => ({
    name: `Município AC ${i + 1}`,
    state: 'AC',
    region: 'Norte' as const,
    population: Math.floor(Math.random() * 58000) + 18000,
    students: Math.floor(Math.random() * 12000) + 3500
  })),

  // Amapá - 2 municípios
  ...Array.from({ length: 2 }, (_, i) => ({
    name: `Município AP ${i + 1}`,
    state: 'AP',
    region: 'Norte' as const,
    population: Math.floor(Math.random() * 55000) + 17000,
    students: Math.floor(Math.random() * 11500) + 3300
  })),

  // Roraima - 1 município
  { name: 'Município RR 1', state: 'RR', region: 'Norte' as const, population: 52000, students: 10500 },

  // Distrito Federal - 1 município
  { name: 'Município DF 1', state: 'DF', region: 'Centro-Oeste' as const, population: 85000, students: 17000 }
];

// Gera dados mock com SUBEXECUÇÃO garantida
const generateMunicipalityData = (
  municipality: typeof municipalities[0],
  index: number
): MunicipalityBudget => {
  const years = [2020, 2021, 2022, 2023, 2024];
  const currentYear = 2024;

  // Budget base varia por tamanho da cidade (R$ por milhão de habitantes)
  const baseBudget = (municipality.population / 1000000) * 1200000000;

  // SUBEXECUÇÃO: Todos gastam menos que deveriam (40% a 85% do orçamento)
  const executionRates: Record<number, number> = {
    2020: 0.72, // Pandemia
    2021: 0.68, // Pandemia continua
    2022: 0.85, // Eleição - execução maior
    2023: 0.78, // Pós-eleição
    2024: 0.55  // SUBEXECUÇÃO FORTE - ano eleitoral com dinheiro sobrando
  };

  // Cada município tem perfil diferente de subexecução
  const profile = index % 10;

  // CARD 1 (index 0): Marcadores BEM PRÓXIMOS - tooltip consolidado (diferença <5%)
  if (index === 0) {
    executionRates[2020] = 0.50; // 50%
    executionRates[2021] = 0.52; // 52% (2% diff)
    executionRates[2022] = 0.54; // 54% (2% diff)
    executionRates[2023] = 0.58;
    executionRates[2024] = 0.45;
  }
  // CARD 2 (index 1): Espaçamento OK - tooltips individuais (diferença ~8-10%)
  else if (index === 1) {
    executionRates[2020] = 0.35; // 35%
    executionRates[2021] = 0.44; // 44% (9% diff)
    executionRates[2022] = 0.54; // 54% (10% diff)
    executionRates[2023] = 0.60;
    executionRates[2024] = 0.48;
  }
  // CARD 3 (index 2): Espaçamento MAIOR que card 2 - tooltips individuais (diferença ~15-18%)
  else if (index === 2) {
    executionRates[2020] = 0.30; // 30%
    executionRates[2021] = 0.48; // 48% (18% diff)
    executionRates[2022] = 0.63; // 63% (15% diff)
    executionRates[2023] = 0.60;
    executionRates[2024] = 0.48;
  }
  else if (profile === 0) {
    // SUBEXECUÇÃO EXTREMA - marcadores espaçados
    executionRates[2020] = 0.25;
    executionRates[2021] = 0.48;
    executionRates[2022] = 0.70;
    executionRates[2023] = 0.62;
    executionRates[2024] = 0.35;
  } else if (profile === 1) {
    // SUBEXECUÇÃO SEVERA - marcadores espaçados
    executionRates[2020] = 0.38;
    executionRates[2021] = 0.60;
    executionRates[2022] = 0.78;
    executionRates[2023] = 0.70;
    executionRates[2024] = 0.45;
  } else if (profile === 2) {
    // SUBEXECUÇÃO ALTA - marcadores espaçados
    executionRates[2020] = 0.30;
    executionRates[2021] = 0.55;
    executionRates[2022] = 0.75;
    executionRates[2023] = 0.75;
    executionRates[2024] = 0.55;
  } else if (profile === 3) {
    // SUBEXECUÇÃO MODERADA - marcadores espaçados
    executionRates[2020] = 0.42;
    executionRates[2021] = 0.65;
    executionRates[2022] = 0.82;
    executionRates[2023] = 0.80;
    executionRates[2024] = 0.65;
  } else if (profile === 4) {
    // SUBEXECUÇÃO LEVE - marcadores espaçados
    executionRates[2020] = 0.50;
    executionRates[2021] = 0.70;
    executionRates[2022] = 0.85;
    executionRates[2023] = 0.85;
    executionRates[2024] = 0.75;
  } else if (profile === 5) {
    // SUBEXECUÇÃO IRREGULAR - marcadores espaçados
    executionRates[2020] = 0.28;
    executionRates[2021] = 0.52;
    executionRates[2022] = 0.78;
    executionRates[2023] = 0.72;
    executionRates[2024] = 0.58;
  } else if (profile === 6) {
    // SUBEXECUÇÃO CRÍTICA - marcadores espaçados
    executionRates[2020] = 0.22;
    executionRates[2021] = 0.45;
    executionRates[2022] = 0.68;
    executionRates[2023] = 0.65;
    executionRates[2024] = 0.38;
  } else if (profile === 7) {
    // SUBEXECUÇÃO MÉDIA - marcadores espaçados
    executionRates[2020] = 0.35;
    executionRates[2021] = 0.58;
    executionRates[2022] = 0.80;
    executionRates[2023] = 0.77;
    executionRates[2024] = 0.62;
  } else if (profile === 8) {
    // SUBEXECUÇÃO VARIÁVEL - marcadores espaçados
    executionRates[2020] = 0.32;
    executionRates[2021] = 0.57;
    executionRates[2022] = 0.73;
    executionRates[2023] = 0.73;
    executionRates[2024] = 0.58;
  } else {
    // SUBEXECUÇÃO CONSTANTE - marcadores espaçados
    executionRates[2020] = 0.40;
    executionRates[2021] = 0.62;
    executionRates[2022] = 0.76;
    executionRates[2023] = 0.68;
    executionRates[2024] = 0.55;
  }

  // Gera histórico
  const history = years.map(year => {
    const yearBudget = baseBudget * (1 + (year - 2020) * 0.06); // Crescimento anual
    const executionRate = executionRates[year] || 0.75;
    const executed = yearBudget * executionRate;
    const available = yearBudget - executed;

    return {
      year,
      totalBudget: yearBudget,
      executed,
      available,
      executionRate: executionRate * 100,
      isElectionYear: year % 4 === 0 || year === 2022
    };
  });

  // Dados do ano atual
  const current = history.find(h => h.year === currentYear)!;

  // Calcula comparações
  const electoralYears = history.filter(h => h.isElectionYear && h.year < currentYear);
  const avgElectoralValue = electoralYears.reduce((sum, h) => sum + h.executed, 0) / electoralYears.length;
  const lastElectoral = electoralYears[electoralYears.length - 1];
  const allYears = history.filter(h => h.year < currentYear);
  const avgAllValue = allYears.reduce((sum, h) => sum + h.executed, 0) / allYears.length;
  const previousYear = history.find(h => h.year === currentYear - 1)!;

  // Função para calcular comparação
  const calculateComparison = (referenceValue: number, referencePeriod: string) => {
    const percentageDeviation = ((current.executed - referenceValue) / referenceValue) * 100;

    // Severidade baseada no desvio negativo (quanto mais negativo, mais crítico)
    let severity: 'critical' | 'high' | 'moderate' | 'normal' = 'normal';
    if (percentageDeviation < -50) severity = 'critical';
    else if (percentageDeviation < -35) severity = 'high';
    else if (percentageDeviation < -20) severity = 'moderate';

    return {
      referenceAmount: referenceValue,
      referencePeriod,
      executedAmount: current.executed,
      percentageDeviation,
      isAnomaly: Math.abs(percentageDeviation) > 15,
      severity
    };
  };

  // Score de severidade (quanto maior, mais prioritário)
  const avgDeviation = ((current.executed - avgElectoralValue) / avgElectoralValue) * 100;
  const severityScore = Math.min(100, Math.max(0, Math.abs(avgDeviation)));

  return {
    id: `mun-${index}`,
    name: municipality.name,
    state: municipality.state,
    region: municipality.region,
    type: 'municipality' as EntityType,
    currentYear,
    totalBudget: current.totalBudget,
    executed: current.executed,
    available: current.available,
    executionRate: current.executionRate,
    population: municipality.population,
    students: municipality.students,
    history,
    comparison: {
      avgElectoral: calculateComparison(avgElectoralValue, 'Média dos Anos Eleitorais'),
      lastElectoral: calculateComparison(lastElectoral.executed, 'Último Ano Eleitoral (2022)'),
      avgAll: calculateComparison(avgAllValue, 'Média de Todos os Anos'),
      previousYear: calculateComparison(previousYear.executed, 'Ano Anterior (2023)')
    },
    severityScore,
    government: 'Lula 3',
    events: ['🗳️ Eleição Municipal']
  };
};

export const municipalityBudgetData: MunicipalityBudget[] = municipalities.map(generateMunicipalityData);
