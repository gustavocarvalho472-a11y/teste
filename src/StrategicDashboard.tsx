import React, { useState, useMemo } from 'react';
import { municipalityBudgetData } from './mockData/municipalityData';
import { ComparisonMode } from './types/municipality';
import MunicipalityDetailCard from './components/MunicipalityDetailCard';
import MunicipalityCard from './components/MunicipalityCard';
import PriorityMunicipalityCard from './components/PriorityMunicipalityCard';
import ComparisonChart from './components/ComparisonChart';
import { formatCurrency } from './utils';
import { COPY, formatCopyTemplate } from './constants/copy';
import { IndicatorType } from './types/budget';

// Paleta roxo e branco elegante
const COLORS = {
  // Backgrounds
  bgPrimary: '#FFFFFF',
  bgSecondary: '#FAFAFA',
  bgTertiary: '#F5F5F7',
  bgPurpleLightest: '#FAF8FF',
  bgPurpleLight: '#F3F0FF',

  // Roxos
  purple900: '#2D1B4E',
  purple800: '#3D2463',
  purple700: '#4C2E7A',
  purple600: '#6941C6',
  purple500: '#7F56D9',
  purple400: '#9E77ED',
  purple300: '#B692F6',
  purple200: '#D6BBFB',
  purple100: '#E9D7FE',
  purple50: '#F4EBFF',

  // Textos
  textPrimary: '#1A1A1A',
  textSecondary: '#525252',
  textTertiary: '#A3A3A3',
  textInverse: '#FFFFFF',
  textPurple: '#6941C6',

  // Borders
  borderLight: '#F0F0F0',
  borderMedium: '#E5E5E5',
  borderDark: '#D4D4D4',
  borderPurple: '#E9D7FE',

  // Accent
  accent: '#6941C6',
  accentHover: '#7F56D9',
  accentLight: '#9E77ED',

  // Gradientes
  gradientStart: '#4C2E7A',
  gradientMid: '#6941C6',
  gradientEnd: '#7F56D9',

  // Gradiente alternativo (mais suave)
  gradientLightStart: '#F4EBFF',
  gradientLightEnd: '#FFFFFF'
};

type TabType = 'visao-rapida' | 'comparador' | 'carometro' | 'clusters' | 'oportunidades';

function StrategicDashboard() {
  const [comparisonMode, setComparisonMode] = useState<ComparisonMode>('avg-electoral');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('Todos');
  const [sortBy, setSortBy] = useState<'deviation' | 'extra' | 'executed'>('extra');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;
  const [activeTab, setActiveTab] = useState<TabType>('comparador');

  // Estados para o gráfico de comparação
  const [selectedMunicipalityForChart, setSelectedMunicipalityForChart] = useState<string>('São Paulo');
  const [selectedMonths, setSelectedMonths] = useState<number[]>([1, 2, 3, 4, 5, 6, 7, 8]);
  const [chartIndicator, setChartIndicator] = useState<IndicatorType>('executed');
  const [chartCurrentYear, setChartCurrentYear] = useState<number>(2024);
  const [chartComparisonYear, setChartComparisonYear] = useState<number>(2022);

  // Filtragem e ordenação
  const filteredAndSortedMunicipalities = useMemo(() => {
    let filtered = municipalityBudgetData;

    // Filtro de busca
    if (searchTerm) {
      filtered = filtered.filter(m =>
        m.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.state.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtro de região
    if (selectedRegion !== 'Todos') {
      filtered = filtered.filter(m => m.region === selectedRegion);
    }

    // Ordenação
    return [...filtered].sort((a, b) => {
      const getComparison = (m: typeof municipalityBudgetData[0]) => {
        switch (comparisonMode) {
          case 'avg-electoral': return m.comparison.avgElectoral;
          case 'last-electoral': return m.comparison.lastElectoral;
          case 'avg-all': return m.comparison.avgAll;
          case 'previous-year': return m.comparison.previousYear;
        }
      };

      const compA = getComparison(a);
      const compB = getComparison(b);

      if (sortBy === 'deviation') {
        return compA.percentageDeviation - compB.percentageDeviation;
      } else if (sortBy === 'extra') {
        const extraA = compA.referenceAmount - compA.executedAmount;
        const extraB = compB.referenceAmount - compB.executedAmount;
        return extraB - extraA;
      } else {
        return compB.executedAmount - compA.executedAmount;
      }
    });
  }, [searchTerm, selectedRegion, sortBy, comparisonMode]);

  // Top 3 para destaque
  const top3 = filteredAndSortedMunicipalities.slice(0, 3);

  // Município selecionado para o gráfico
  const selectedMunicipalityData = useMemo(() => {
    return municipalityBudgetData.find(m => m.name === selectedMunicipalityForChart);
  }, [selectedMunicipalityForChart]);

  // Converter dados do município para formato mensal para o ComparisonChart
  const municipalityChartData = useMemo(() => {
    if (!selectedMunicipalityData || !selectedMunicipalityData.history) {
      return { current: [], comparison: [] };
    }

    // Simula dados mensais baseado no total do ano
    const currentYearData = Array.from({ length: 12 }, (_, i) => {
      const month = i + 1;
      const monthData = selectedMunicipalityData.history?.find(h => h.year === chartCurrentYear);

      if (!monthData || !monthData.totalBudget) {
        return { month, year: chartCurrentYear, planned: 0, executed: 0, available: 0 };
      }

      const monthlyPlanned = monthData.totalBudget / 12;
      const monthlyExecuted = monthData.executed / 12;
      return {
        month,
        year: chartCurrentYear,
        planned: monthlyPlanned,
        executed: monthlyExecuted,
        available: monthlyPlanned - monthlyExecuted
      };
    });

    const comparisonYearData = Array.from({ length: 12 }, (_, i) => {
      const month = i + 1;
      const monthData = selectedMunicipalityData.history?.find(h => h.year === chartComparisonYear);

      if (!monthData || !monthData.totalBudget) {
        return { month, year: chartComparisonYear, planned: 0, executed: 0, available: 0 };
      }

      const monthlyPlanned = monthData.totalBudget / 12;
      const monthlyExecuted = monthData.executed / 12;
      return {
        month,
        year: chartComparisonYear,
        planned: monthlyPlanned,
        executed: monthlyExecuted,
        available: monthlyPlanned - monthlyExecuted
      };
    });

    return { current: currentYearData, comparison: comparisonYearData };
  }, [selectedMunicipalityData, chartCurrentYear, chartComparisonYear]);

  // Paginação
  const totalPages = Math.ceil(filteredAndSortedMunicipalities.length / itemsPerPage);
  const paginatedMunicipalities = filteredAndSortedMunicipalities.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Estatísticas gerais detalhadas com simulação realista
  const stats = useMemo(() => {
    const getComparison = (mun: typeof filteredAndSortedMunicipalities[0]) => {
      switch (comparisonMode) {
        case 'avg-electoral': return mun.comparison.avgElectoral;
        case 'last-electoral': return mun.comparison.lastElectoral;
        case 'avg-all': return mun.comparison.avgAll;
        case 'previous-year': return mun.comparison.previousYear;
      }
    };

    // Usar dados simulados realistas
    const totalBudget = COPY.simulation.budgetTotal;
    const totalExecuted = COPY.simulation.executed;
    const totalExtra = COPY.simulation.available;
    const totalAboveAverage = COPY.simulation.aboveAverage;
    const avgDeviation = Math.abs(COPY.simulation.deviationPercent);

    // Contar por severidade na amostra atual
    const critical = filteredAndSortedMunicipalities.filter(m => getComparison(m).severity === 'critical').length;
    const high = filteredAndSortedMunicipalities.filter(m => getComparison(m).severity === 'high').length;

    // Ranking por estado
    const byState = filteredAndSortedMunicipalities.reduce((acc, m) => {
      if (!acc[m.state]) {
        acc[m.state] = { count: 0, totalExtra: 0 };
      }
      acc[m.state].count++;
      acc[m.state].totalExtra += (getComparison(m).referenceAmount - getComparison(m).executedAmount);
      return acc;
    }, {} as Record<string, { count: number; totalExtra: number }>);

    const stateRanking = Object.entries(byState)
      .map(([state, data]) => ({
        state,
        count: data.count,
        totalExtra: data.totalExtra
      }))
      .sort((a, b) => b.totalExtra - a.totalExtra)
      .slice(0, 5);

    return {
      totalExtra,
      totalBudget,
      totalExecuted,
      totalAboveAverage,
      avgDeviation,
      critical,
      high,
      stateRanking,
      executionRate: COPY.simulation.currentExecutionRate,
      historicalExecutionRate: COPY.simulation.historicalExecutionRate,
      totalMunicipalities: COPY.simulation.totalMunicipalities,
      withDeviation: COPY.simulation.withDeviation
    };
  }, [filteredAndSortedMunicipalities, comparisonMode]);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#FFFFFF',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Background roxo apenas no topo com curva */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '520px',
        background: 'linear-gradient(180deg, #E5D4FF 0%, #DDD6FE 100%)',
        borderBottomLeftRadius: '32px',
        borderBottomRightRadius: '32px',
        zIndex: 0
      }} />

      {/* Container principal com padding */}
      <div style={{
        position: 'relative',
        zIndex: 1,
        padding: '20px 40px'
      }}>
        {/* Container centralizado para o menu */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          marginBottom: '32px'
        }}>
          {/* Menu flutuante */}
          <div style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '12px',
            padding: '8px 32px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '16px'
          }}>
          {/* Logo codora */}
          <div style={{
            paddingRight: '12px',
            borderRight: '1px solid #E5E7EB',
            display: 'flex',
            alignItems: 'center'
          }}>
            <svg width="50" height="25" viewBox="0 0 50 25" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M27.5561 2.73386C28.311 2.73386 28.923 2.12188 28.923 1.36696C28.923 0.612042 28.311 6.10352e-05 27.5561 6.10352e-05C26.8012 6.10352e-05 26.1892 0.612042 26.1892 1.36696C26.1892 2.12188 26.8012 2.73386 27.5561 2.73386Z" fill="#6640E7"/>
              <path d="M48.5018 2.46703H46.7325C46.7222 2.46733 46.7121 2.46978 46.7028 2.47422C46.6935 2.47865 46.6852 2.48498 46.6785 2.4928C46.6718 2.50061 46.6668 2.50974 46.6638 2.5196C46.6608 2.52946 46.66 2.53983 46.6612 2.55005L46.5778 3.29135C46.578 3.30721 46.5736 3.32279 46.5652 3.33626C46.5569 3.34972 46.5448 3.36051 46.5305 3.36733C46.5162 3.37416 46.5002 3.37674 46.4844 3.37477C46.4687 3.3728 46.4539 3.36636 46.4417 3.35622C46.1241 3.10081 45.7662 2.81681 45.4059 2.6612C44.8611 2.42568 44.2755 2.29855 43.682 2.28693H43.6058C43.0336 2.28795 42.4667 2.39565 41.934 2.60449C41.3737 2.82225 40.8543 3.23191 40.4324 3.64248C40.0009 4.06381 39.6569 4.56627 39.4203 5.12098C39.0655 5.95916 38.9723 6.88499 39.1529 7.77705C39.3335 8.66912 39.7795 9.48578 40.4324 10.1199C40.8543 10.5305 41.3737 10.9397 41.9349 11.1602C42.4918 11.3771 43.0854 11.484 43.6829 11.475C44.2764 11.4635 44.8619 11.3365 45.4068 11.1012C45.7698 10.9456 46.1114 10.6612 46.4303 10.4058C46.4421 10.3964 46.4562 10.3904 46.4711 10.3883C46.4861 10.3862 46.5012 10.3882 46.5152 10.394C46.529 10.3997 46.541 10.4092 46.5498 10.4212C46.5587 10.4333 46.5641 10.4475 46.5655 10.4625L46.634 11.1334C46.636 11.154 46.6457 11.1731 46.661 11.1869C46.6764 11.2008 46.6964 11.2084 46.717 11.2083H48.5027C48.5247 11.2083 48.5458 11.1995 48.5614 11.184C48.5769 11.1684 48.5857 11.1473 48.5857 11.1253V2.55096C48.5858 2.53992 48.5836 2.52898 48.5794 2.51877C48.5752 2.50856 48.5691 2.49929 48.5612 2.49148C48.5534 2.48367 48.5442 2.47749 48.534 2.4733C48.5237 2.4691 48.5128 2.46697 48.5018 2.46703ZM43.7414 9.51611C43.2148 9.51467 42.7005 9.35723 42.2633 9.06365C41.8261 8.77007 41.4858 8.35353 41.2852 7.86663C41.0846 7.37974 41.0328 6.84432 41.1363 6.32799C41.2398 5.81167 41.494 5.3376 41.8668 4.96565C42.2395 4.5937 42.7142 4.34055 43.2307 4.23818C43.7473 4.13581 44.2826 4.1888 44.769 4.39046C45.2555 4.59213 45.6713 4.93342 45.9639 5.37124C46.2565 5.80906 46.4128 6.32376 46.4131 6.85036C46.4118 7.55798 46.1297 8.23615 45.6288 8.73595C45.1278 9.23576 44.4491 9.51635 43.7414 9.51611Z" fill="#2E3137"/>
              <path d="M36.753 3.55957C36.3479 3.16488 35.8574 2.79197 35.3339 2.58283C34.2718 2.15708 33.0842 2.16948 32.0312 2.6173C31.7903 2.71983 31.5549 2.9013 31.3312 3.05056C31.319 3.0586 31.305 3.06332 31.2904 3.06422C31.2758 3.06513 31.2613 3.0622 31.2482 3.05573C31.2351 3.04926 31.2239 3.03946 31.2158 3.02733C31.2077 3.0152 31.2029 3.00115 31.2019 2.98659L31.1529 2.53746C31.1499 2.51779 31.1399 2.49986 31.1247 2.48695C31.1095 2.47405 31.0903 2.46702 31.0704 2.46714H29.3396C29.3176 2.46726 29.2966 2.47605 29.281 2.49159C29.2655 2.50713 29.2567 2.52818 29.2566 2.55016V11.1245C29.2566 11.1354 29.2587 11.1462 29.2629 11.1562C29.2671 11.1663 29.2732 11.1755 29.2809 11.1832C29.2886 11.1909 29.2978 11.197 29.3078 11.2012C29.3179 11.2053 29.3287 11.2075 29.3396 11.2075H31.1806C31.2027 11.2075 31.2238 11.1988 31.2395 11.1832C31.2551 11.1676 31.2639 11.1465 31.2641 11.1245C31.2641 11.1245 31.2604 5.88597 31.2641 5.8769C31.4002 5.50353 31.5644 5.21954 31.8461 4.95051C32.3383 4.48069 32.9959 4.2238 33.6762 4.23553C34.344 4.24778 34.9011 4.52906 35.3611 5.00677C35.8184 5.48101 36.0687 6.11738 36.0571 6.77607V11.1267C36.0571 11.1375 36.0593 11.1482 36.0635 11.1581C36.0678 11.168 36.0739 11.177 36.0816 11.1845C36.0894 11.192 36.0985 11.1979 36.1086 11.2019C36.1186 11.2058 36.1293 11.2077 36.1401 11.2075H37.9811C38.0264 11.2075 38.0641 11.1521 38.0641 11.1063V6.62364C38.0579 6.05142 37.9388 5.48605 37.7136 4.95994C37.4885 4.43383 37.1617 3.95733 36.7521 3.55776L36.753 3.55957Z" fill="#2E3137"/>
              <path d="M4.62241 4.18629C5.02667 4.1856 5.42592 4.27574 5.79066 4.45006C6.15541 4.62438 6.47632 4.87843 6.7297 5.19343C6.74294 5.20951 6.76182 5.21992 6.78248 5.22253C6.80314 5.22515 6.82402 5.21977 6.84084 5.2075L8.26944 4.194C8.27844 4.18759 8.28606 4.17942 8.29183 4.16998C8.2976 4.16055 8.3014 4.15005 8.30301 4.13911C8.30477 4.12762 8.30414 4.11589 8.30118 4.10466C8.29821 4.09342 8.29297 4.08291 8.28577 4.07378C7.85165 3.51565 7.2962 3.06364 6.6615 2.75199C6.0268 2.44033 5.3295 2.27722 4.62241 2.27499C2.07371 2.27499 0 4.34145 0 6.88107C0 9.4207 2.07371 11.4867 4.62241 11.4867C5.32945 11.4845 6.02671 11.3214 6.66139 11.0098C7.29608 10.6983 7.85156 10.2464 8.28577 9.68837C8.29296 9.67914 8.29819 9.66856 8.30115 9.65725C8.30412 9.64594 8.30475 9.63414 8.30301 9.62258C8.3014 9.61164 8.2976 9.60115 8.29183 9.59171C8.28606 9.58228 8.27844 9.57411 8.26944 9.56769L6.84084 8.5542C6.82389 8.54219 6.80303 8.53702 6.78243 8.53971C6.76183 8.5424 6.743 8.55276 6.7297 8.56872C6.21206 9.20929 5.444 9.51597 4.62241 9.51597C3.13121 9.51597 2.00748 8.36683 2.00748 6.88107C2.00748 5.39531 3.1303 4.18629 4.62241 4.18629Z" fill="#2E3137"/>
              <path d="M26.1303 10.3097C27.5617 9.61874 28.2576 8.50271 28.2576 6.899C28.2576 4.67059 26.7945 2.2716 23.5848 2.2716C21.3074 2.2716 18.8567 3.7197 18.8567 6.899C18.8567 8.28995 19.3031 9.4536 20.1474 10.2634C20.983 11.0646 22.1716 11.4883 23.5848 11.4883C25.1994 11.4883 26.2392 12.2024 26.2392 13.3987C26.2392 14.5664 24.9327 15.2533 23.5494 15.2533C22.1662 15.2533 20.924 14.536 20.88 13.2063C20.8797 13.1845 20.8708 13.1636 20.8553 13.1482C20.8398 13.1328 20.8189 13.124 20.797 13.1238H18.9697C18.9479 13.1235 18.9269 13.1319 18.9113 13.147C18.8957 13.1621 18.8867 13.1828 18.8862 13.2045C18.8812 14.3387 19.2419 15.305 19.9296 15.9932C20.7408 16.8053 21.9915 17.2344 23.5472 17.2344C25.8155 17.2344 28.2576 16.034 28.2576 13.3987C28.2576 12.4292 27.8897 11.1326 26.1367 10.4621C26.1215 10.4563 26.1084 10.4462 26.0989 10.433C26.0894 10.4199 26.084 10.4042 26.0833 10.388C26.0826 10.3718 26.0867 10.3557 26.0951 10.3418C26.1034 10.3279 26.1157 10.3167 26.1303 10.3097ZM23.5825 9.49851C21.9806 9.49851 20.8605 8.40971 20.8605 6.85318C20.8605 5.23495 21.9289 4.18925 23.5825 4.18925C25.1282 4.18925 26.2501 5.30935 26.2501 6.85318C26.2496 8.41062 25.1527 9.49851 23.5821 9.49851H23.5825Z" fill="#2E3137"/>
              <path d="M13.2334 2.27499C10.6842 2.27499 8.61096 4.34145 8.61096 6.88107C8.61096 9.4207 10.6842 11.4867 13.2334 11.4867C15.7825 11.4867 17.8558 9.4207 17.8558 6.88107C17.8558 4.34145 15.7821 2.27499 13.2334 2.27499ZM13.2334 9.4883C12.5413 9.4889 11.8772 9.21492 11.3869 8.72646C10.8966 8.23801 10.62 7.57499 10.618 6.88289C10.618 5.44613 11.7912 4.18947 13.2334 4.18947C14.6756 4.18947 15.8483 5.44613 15.8483 6.88289C15.8458 7.57459 15.5691 8.23708 15.0789 8.72513C14.5888 9.21318 13.9251 9.48697 13.2334 9.48648V9.4883Z" fill="#2E3137"/>
              <path d="M33.9152 17.1197C34.3401 17.2103 34.6814 17.4227 34.9392 17.7571C35.1969 18.0845 35.3258 18.4606 35.3258 18.8855C35.3258 19.4985 35.1098 19.9861 34.678 20.3483C34.2531 20.7036 33.6575 20.8812 32.8913 20.8812H29.4746V13.5463H32.7763C33.5217 13.5463 34.1033 13.717 34.5212 14.0583C34.9461 14.3996 35.1586 14.8629 35.1586 15.448C35.1586 15.8798 35.0437 16.2386 34.8138 16.5242C34.5909 16.8098 34.2914 17.0083 33.9152 17.1197ZM31.2613 16.5137H32.4315C32.7241 16.5137 32.947 16.451 33.1002 16.3257C33.2605 16.1933 33.3406 16.0017 33.3406 15.751C33.3406 15.5002 33.2605 15.3087 33.1002 15.1763C32.947 15.044 32.7241 14.9778 32.4315 14.9778H31.2613V16.5137ZM32.5778 19.4393C32.8773 19.4393 33.1072 19.3731 33.2674 19.2408C33.4346 19.1015 33.5182 18.903 33.5182 18.6452C33.5182 18.3875 33.4311 18.1855 33.257 18.0392C33.0898 17.8929 32.8564 17.8198 32.5569 17.8198H31.2613V19.4393H32.5778ZM47.2002 15.8659C47.0678 15.6221 46.8763 15.4375 46.6255 15.3121C46.3817 15.1798 46.0926 15.1136 45.7583 15.1136C45.1801 15.1136 44.7169 15.3052 44.3686 15.6883C44.0204 16.0644 43.8462 16.5694 43.8462 17.2033C43.8462 17.879 44.0273 18.4084 44.3895 18.7915C44.7587 19.1676 45.2637 19.3557 45.9046 19.3557C46.3434 19.3557 46.7126 19.2443 47.0121 19.0214C47.3186 18.7985 47.5415 18.478 47.6808 18.0601H45.4135V16.7436H49.3003V18.4049C49.168 18.8507 48.9416 19.2652 48.6212 19.6483C48.3077 20.0314 47.9072 20.3414 47.4196 20.5782C46.932 20.815 46.3817 20.9334 45.7687 20.9334C45.0443 20.9334 44.3965 20.7767 43.8253 20.4633C43.2611 20.1428 42.8188 19.7005 42.4984 19.1363C42.1849 18.5721 42.0282 17.9278 42.0282 17.2033C42.0282 16.4789 42.1849 15.8346 42.4984 15.2704C42.8188 14.6992 43.2611 14.2568 43.8253 13.9434C44.3895 13.623 45.0339 13.4628 45.7583 13.4628C46.636 13.4628 47.3743 13.6752 47.9734 14.1001C48.5794 14.525 48.9799 15.1136 49.175 15.8659H47.2002Z" fill="#2E3137"/>
              <path d="M36.1217 19.4498C36.3586 19.2617 36.4665 19.1746 36.4456 19.1885C37.1283 18.6243 37.6646 18.1611 38.0547 17.7989C38.4518 17.4367 38.7861 17.057 39.0578 16.66C39.3294 16.263 39.4653 15.8764 39.4653 15.5002C39.4653 15.2146 39.3991 14.9917 39.2667 14.8315C39.1344 14.6713 38.9359 14.5912 38.6712 14.5912C38.4065 14.5912 38.1975 14.6922 38.0443 14.8942C37.898 15.0892 37.8248 15.3679 37.8248 15.7301H36.1008C36.1148 15.138 36.2402 14.6434 36.477 14.2464C36.7208 13.8494 37.0377 13.5568 37.4278 13.3687C37.8248 13.1806 38.2637 13.0866 38.7443 13.0866C39.5732 13.0866 40.1967 13.2991 40.6146 13.724C41.0395 14.1489 41.252 14.7026 41.252 15.3853C41.252 16.1306 40.9977 16.8237 40.4892 17.4645C39.9807 18.0984 39.3329 18.7184 38.5458 19.3244H41.3669V20.7767H36.1217V19.4498Z" fill="#8725FF"/>
            </svg>
          </div>

          {/* Navigation Tabs */}
          <nav style={{
            display: 'flex',
            gap: '2px'
          }}>
            {[
              { id: 'visao-rapida' as TabType, label: 'Visão rápida', icon: 'visibility' },
              { id: 'comparador' as TabType, label: 'Comparador', icon: 'compare_arrows' },
              { id: 'carometro' as TabType, label: 'Carômetro', icon: 'group' },
              { id: 'clusters' as TabType, label: 'Clusters', icon: 'stars' },
              { id: 'oportunidades' as TabType, label: 'Oportunidades', icon: 'emoji_events' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '6px 10px',
                  borderRadius: '6px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  color: activeTab === tab.id ? '#7C3AED' : '#6B7280',
                  fontSize: '13px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
                onMouseEnter={(e) => {
                  if (activeTab !== tab.id) {
                    e.currentTarget.style.color = '#111827';
                  }
                }}
                onMouseLeave={(e) => {
                  if (activeTab !== tab.id) {
                    e.currentTarget.style.color = '#6B7280';
                  }
                }}
              >
                <span className="material-icons" style={{ fontSize: '16px' }}>
                  {tab.icon}
                </span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>

          {/* Ícones da direita */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            paddingLeft: '12px',
            borderLeft: '1px solid #E5E7EB'
          }}>
            <button style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '6px',
              display: 'flex',
              alignItems: 'center',
              color: '#6B7280',
              borderRadius: '6px'
            }}>
              <span className="material-icons" style={{ fontSize: '20px' }}>
                notifications_none
              </span>
            </button>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: '#FEF3C7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer'
            }}>
              <span style={{ fontSize: '14px' }}>👤</span>
            </div>
          </div>
          </div>
        </div>

      {/* Hero Section - Card branco arredondado */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        padding: '40px 32px 32px 32px',
        marginBottom: '20px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ marginBottom: '28px' }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#9CA3AF',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '8px'
          }}>
            INTELIGÊNCIA ORÇAMENTÁRIA
          </div>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#111827',
            margin: 0,
            marginBottom: '8px',
            lineHeight: '1.3'
          }}>
            Painel Estratégico de Gestão Orçamentária
          </h1>
          <p style={{
            fontSize: '14px',
            color: '#6B7280',
            margin: 0,
            lineHeight: '1.6'
          }}>
            Análise consolidada dos 5.570 municípios brasileiros · Identificação de oportunidades e recursos disponíveis
          </p>
        </div>

        {/* Stats Grid - 4 Cards Repensados */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '12px'
        }}>
          {/* Card 1: Verde Escuro */}
          <div style={{
            background: '#047857',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{
              fontSize: '10px',
              fontWeight: '600',
              color: 'rgba(255, 255, 255, 0.7)',
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              MUNICÍPIOS IDENTIFICADOS
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#FFFFFF',
              lineHeight: '1',
              marginBottom: '4px'
            }}>
              {COPY.simulation.withDeviation}
            </div>
            <div style={{
              fontSize: '13px',
              color: 'rgba(255, 255, 255, 0.8)',
              fontWeight: '500',
              lineHeight: '1.4'
            }}>
              de {COPY.simulation.totalMunicipalities.toLocaleString('pt-BR')} municípios
            </div>
          </div>

          {/* Card 2: Lilás */}
          <div style={{
            background: '#DDD6FE',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{
              fontSize: '10px',
              fontWeight: '600',
              color: '#6B21A8',
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              ORÇAMENTO DISPONÍVEL
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#6B21A8',
              lineHeight: '1',
              marginBottom: '4px'
            }}>
              {formatCurrency(COPY.simulation.availableTotal, true)}
            </div>
            <div style={{
              fontSize: '13px',
              color: '#7C3AED',
              fontWeight: '500',
              lineHeight: '1.4'
            }}>
              não executados até agosto
            </div>
          </div>

          {/* Card 3: Coral/Salmão */}
          <div style={{
            background: '#FDA4AF',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{
              fontSize: '10px',
              fontWeight: '600',
              color: '#9F1239',
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              OPORTUNIDADE IDENTIFICADA
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#9F1239',
              lineHeight: '1',
              marginBottom: '4px'
            }}>
              {formatCurrency(COPY.simulation.opportunityValue, true)}
            </div>
            <div style={{
              fontSize: '13px',
              color: '#BE123C',
              fontWeight: '500',
              lineHeight: '1.4'
            }}>
              acima da média histórica
            </div>
          </div>

          {/* Card 4: Roxo Escuro */}
          <div style={{
            background: '#7C3AED',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{
              fontSize: '10px',
              fontWeight: '600',
              color: 'rgba(255, 255, 255, 0.7)',
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              EXECUÇÃO MÉDIA
            </div>
            <div style={{
              fontSize: '36px',
              fontWeight: '700',
              color: '#FFFFFF',
              lineHeight: '1',
              marginBottom: '4px'
            }}>
              {COPY.simulation.actualExecutionRateDeviation}%
            </div>
            <div style={{
              fontSize: '13px',
              color: 'rgba(255, 255, 255, 0.8)',
              fontWeight: '500',
              lineHeight: '1.4'
            }}>
              executado até agosto/2025
            </div>
          </div>
        </div>

        {/* Contexto Adicional */}
        <div style={{
          backgroundColor: 'rgba(255, 255, 255, 0.15)',
          borderRadius: '8px',
          padding: '12px 16px',
          border: '1px solid rgba(255, 255, 255, 0.25)',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{
            fontSize: '13px',
            color: COLORS.purple100,
            textAlign: 'center',
            lineHeight: '1.6'
          }}>
            {COPY.header.context}
          </div>
        </div>
      </div>

      {/* Ranking de Estados */}
      <div style={{
        backgroundColor: COLORS.bgPrimary,
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '32px',
        border: `2px solid ${COLORS.borderLight}`,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)'
      }}>
        <div style={{
          marginBottom: '16px'
        }}>
          <div style={{
            fontSize: '18px',
            fontWeight: '700',
            color: COLORS.textPrimary,
            marginBottom: '4px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span>{COPY.sections.topEstados.title}</span>
          </div>
          <div style={{
            fontSize: '13px',
            color: COLORS.textSecondary,
            fontWeight: '400'
          }}>
            {COPY.sections.topEstados.subtitle}
          </div>
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '12px'
        }}>
          {stats.stateRanking.map((state, index) => (
            <div key={state.state} style={{
              backgroundColor: COLORS.bgPurpleLight,
              borderRadius: '8px',
              padding: '12px',
              border: `2px solid ${COLORS.borderPurple}`
            }}>
              <div style={{
                fontSize: '11px',
                color: COLORS.purple600,
                fontWeight: '600',
                marginBottom: '4px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <span>{index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}º`}</span>
                <span>{state.state}</span>
              </div>
              <div style={{
                fontSize: '18px',
                fontWeight: '700',
                color: COLORS.textPrimary,
                marginBottom: '2px'
              }}>
                {formatCurrency(state.totalExtra, true)}
              </div>
              <div style={{
                fontSize: '10px',
                color: COLORS.textSecondary
              }}>
                {state.count} município{state.count > 1 ? 's' : ''}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Municípios Prioritários */}
      <div style={{
        marginBottom: '32px',
        backgroundColor: '#FFFFFF',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)'
      }}>
        <div style={{
          marginBottom: '28px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start'
        }}>
          <div>
            <h2 style={{
              fontSize: '26px',
              fontWeight: '700',
              color: '#1a1a1a',
              margin: 0,
              marginBottom: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span className="material-icons" style={{
                fontSize: '28px',
                color: '#6941C6'
              }}>
                location_city
              </span>
              <span>{COPY.sections.prioritarios.title}</span>
            </h2>
            <p style={{
              fontSize: '15px',
              color: '#6b7280',
              margin: 0,
              maxWidth: '700px',
              lineHeight: '1.6'
            }}>
              {COPY.sections.prioritarios.subtitle}
            </p>
          </div>
          <div style={{
            textAlign: 'right',
            backgroundColor: '#F9FAFB',
            padding: '16px 20px',
            borderRadius: '12px',
            border: '1px solid #E5E7EB'
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#7C3AED',
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              {formatCopyTemplate(COPY.sections.prioritarios.showing, {
                count: top3.length
              })}
            </div>
            <div style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1a1a1a',
              marginBottom: '4px'
            }}>
              {formatCurrency(
                top3.reduce((sum, m) => {
                  const getComparison = (mun: typeof municipalityBudgetData[0]) => {
                    switch (comparisonMode) {
                      case 'avg-electoral': return mun.comparison.avgElectoral;
                      case 'last-electoral': return mun.comparison.lastElectoral;
                      case 'avg-all': return mun.comparison.avgAll;
                      case 'previous-year': return mun.comparison.previousYear;
                    }
                  };
                  const comp = getComparison(m);
                  return sum + (comp.referenceAmount - comp.executedAmount);
                }, 0),
                true
              )}
            </div>
            <div style={{
              fontSize: '12px',
              color: '#6b7280'
            }}>
              Oportunidade Total
            </div>
          </div>
        </div>

        {/* Grid de Municípios */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: '20px',
          marginBottom: '16px'
        }}>
          {top3.slice(0, 12).map((mun, index) => (
            <PriorityMunicipalityCard
              key={mun.id}
              municipality={mun}
              comparisonMode={comparisonMode}
              rank={index + 1}
            />
          ))}
        </div>

        {/* Botão Ver Todos */}
        {filteredAndSortedMunicipalities.length > 12 && (
          <div style={{ textAlign: 'center' }}>
            <button
              onClick={() => setCurrentPage(1)}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                border: `2px solid ${COLORS.purple600}`,
                backgroundColor: 'transparent',
                color: COLORS.purple600,
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = COLORS.purple600;
                e.currentTarget.style.color = '#FFFFFF';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = COLORS.purple600;
              }}
            >
              {formatCopyTemplate(COPY.sections.prioritarios.viewAll, {
                total: filteredAndSortedMunicipalities.length
              })}
            </button>
          </div>
        )}
      </div>

      {/* Gráfico de Comparação Dinâmica */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <div>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#2e3138',
              margin: 0,
              marginBottom: '4px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span className="material-icons" style={{ fontSize: '24px', color: '#6941C6' }}>show_chart</span>
              <span>Comparação Dinâmica</span>
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              Selecione um município e compare períodos
            </p>
          </div>

          {/* Seletor de Município */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <label style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#6b7280'
            }}>
              Município:
            </label>
            <select
              value={selectedMunicipalityForChart}
              onChange={(e) => setSelectedMunicipalityForChart(e.target.value)}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '2px solid #e1cdfe',
                backgroundColor: '#ffffff',
                color: '#2e3138',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                minWidth: '200px'
              }}
            >
              {municipalityBudgetData.map(m => (
                <option key={m.id} value={m.name}>{m.name}</option>
              ))}
            </select>
          </div>
        </div>

        <ComparisonChart
          currentData={municipalityChartData.current}
          comparisonData={municipalityChartData.comparison}
          indicator={chartIndicator}
          onIndicatorChange={setChartIndicator}
          selectedMonths={selectedMonths}
          onMonthToggle={(month) => {
            setSelectedMonths(prev =>
              prev.includes(month)
                ? prev.filter(m => m !== month)
                : [...prev, month].sort((a, b) => a - b)
            );
          }}
          currentLabel={`${chartCurrentYear}`}
          comparisonLabel={`${chartComparisonYear} 🗳️`}
        />
      </div>

      {/* Grid de Municípios com Paginação */}
      <div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px'
        }}>
          <h2 style={{
            fontSize: '20px',
            fontWeight: '700',
            color: '#2e3138',
            margin: 0,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span className="material-icons" style={{ fontSize: '24px', color: '#6941C6' }}>location_city</span>
            <span>Municípios ({filteredAndSortedMunicipalities.length})</span>
          </h2>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <label style={{
                fontSize: '13px',
                fontWeight: '600',
                color: '#6b7280'
              }}>
                Ordenar:
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'deviation' | 'extra' | 'executed')}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: '2px solid #e1cdfe',
                  backgroundColor: '#ffffff',
                  color: '#2e3138',
                  fontSize: '13px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                <option value="extra">Maior verba sobrando</option>
                <option value="executed">Maior executado</option>
                <option value="deviation">Maior desvio %</option>
              </select>
            </div>
            <div style={{
              fontSize: '14px',
              color: '#6b7280',
              fontWeight: '600'
            }}>
              Página {currentPage} de {totalPages}
            </div>
          </div>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '20px',
          marginBottom: '24px'
        }}>
          {paginatedMunicipalities.map(municipality => (
            <MunicipalityDetailCard
              key={municipality.id}
              municipality={municipality}
              mode={comparisonMode}
              onSelect={() => {}}
            />
          ))}
        </div>

        {/* Paginação */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '8px',
          marginTop: '32px'
        }}>
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            style={{
              padding: '10px 20px',
              fontSize: '14px',
              fontWeight: '600',
              border: '2px solid #e1cdfe',
              borderRadius: '8px',
              backgroundColor: currentPage === 1 ? '#f3f4f6' : '#ffffff',
              color: currentPage === 1 ? '#9ca3af' : '#9755fe',
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s'
            }}
          >
            ← Anterior
          </button>

          <div style={{
            display: 'flex',
            gap: '6px'
          }}>
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }

              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  style={{
                    padding: '10px 16px',
                    fontSize: '14px',
                    fontWeight: '600',
                    border: '2px solid',
                    borderColor: currentPage === pageNum ? '#9755fe' : '#e1cdfe',
                    borderRadius: '8px',
                    backgroundColor: currentPage === pageNum ? '#9755fe' : '#ffffff',
                    color: currentPage === pageNum ? '#ffffff' : '#6b7280',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    minWidth: '44px'
                  }}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            style={{
              padding: '10px 20px',
              fontSize: '14px',
              fontWeight: '600',
              border: '2px solid #e1cdfe',
              borderRadius: '8px',
              backgroundColor: currentPage === totalPages ? '#f3f4f6' : '#ffffff',
              color: currentPage === totalPages ? '#9ca3af' : '#9755fe',
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s'
            }}
          >
            Próximo →
          </button>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        marginTop: '48px',
        padding: '16px',
        textAlign: 'center',
        color: '#6b7280',
        fontSize: '13px'
      }}>
        <p style={{ margin: 0 }}>
          Painel Estratégico de Gestão Orçamentária · Visão Consolidada Nacional
        </p>
      </div>
      </div>
    </div>
  );
}

export default StrategicDashboard;
