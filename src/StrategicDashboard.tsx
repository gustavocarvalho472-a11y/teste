import React, { useState, useMemo } from 'react';
import { municipalityBudgetData } from './mockData/municipalityData';
import { ComparisonMode } from './types/municipality';
import MunicipalityDetailCard from './components/MunicipalityDetailCard';
import AdvancedFilters from './components/AdvancedFilters';
import MunicipalityCard from './components/MunicipalityCard';
import PriorityMunicipalityCard from './components/PriorityMunicipalityCard';
import MunicipalityComparisonChart from './components/MunicipalityComparisonChart';
import { formatCurrency } from './utils';
import { COPY, formatCopyTemplate } from './constants/copy';

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

function StrategicDashboard() {
  const [comparisonMode, setComparisonMode] = useState<ComparisonMode>('avg-electoral');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('Todos');
  const [sortBy, setSortBy] = useState<'deviation' | 'extra' | 'executed'>('extra');
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');
  const [currentPeriod, setCurrentPeriod] = useState<number>(2024);
  const [comparisonPeriod, setComparisonPeriod] = useState<number>(2020);
  const [comparisonMetric, setComparisonMetric] = useState<'executed' | 'deviation' | 'extra'>('extra');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

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

  // Dados de comparação para o gráfico (Top 10)
  const comparisonData = useMemo(() => {
    const getComparison = (m: typeof municipalityBudgetData[0]) => {
      switch (comparisonMode) {
        case 'avg-electoral': return m.comparison.avgElectoral;
        case 'last-electoral': return m.comparison.lastElectoral;
        case 'avg-all': return m.comparison.avgAll;
        case 'previous-year': return m.comparison.previousYear;
      }
    };

    return filteredAndSortedMunicipalities.slice(0, 10).map(m => {
      const comp = getComparison(m);

      // Pegar o valor executado do período de comparação dos dados históricos
      const comparisonYearData = m.history.find(h => h.year === comparisonPeriod);

      return {
        name: m.name,
        executed: comp.executedAmount,
        reference: comp.referenceAmount,
        deviation: comp.percentageDeviation,
        comparisonExecuted: comparisonYearData ? comparisonYearData.executed : undefined
      };
    });
  }, [filteredAndSortedMunicipalities, comparisonMode, comparisonPeriod]);

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
      backgroundColor: COLORS.bgPurpleLightest,
      padding: '32px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Hero Section - Resumo Brasil */}
      <div style={{
        borderRadius: '16px',
        padding: '40px',
        marginBottom: '32px',
        boxShadow: '0 8px 24px rgba(105, 65, 198, 0.15)',
        background: `linear-gradient(135deg, ${COLORS.gradientStart} 0%, ${COLORS.gradientMid} 50%, ${COLORS.gradientEnd} 100%)`,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '24px', position: 'relative', zIndex: 1 }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: COLORS.purple200,
            textTransform: 'uppercase',
            letterSpacing: '1.5px',
            marginBottom: '8px'
          }}>
            {COPY.header.eyebrow}
          </div>
          <h1 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: COLORS.textInverse,
            margin: 0,
            lineHeight: '1.2',
            textShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
          }}>
            {COPY.header.title}
          </h1>
          <p style={{
            fontSize: '15px',
            color: COLORS.purple100,
            marginTop: '12px',
            margin: 0,
            maxWidth: '800px',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}>
            {COPY.header.subtitle}
          </p>
        </div>

        {/* Stats Grid - 4 Cards Repensados */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '16px',
          marginBottom: '16px'
        }}>
          {/* Card 1: Municípios Fora do Padrão (DESTAQUE) */}
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '12px',
            padding: '20px',
            border: `2px solid ${COLORS.borderPurple}`,
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 12px rgba(105, 65, 198, 0.08)'
          }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: COLORS.purple600,
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>🎯</span>
              <span>MUNICÍPIOS FORA DO PADRÃO</span>
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: '8px',
              marginBottom: '8px'
            }}>
              <div style={{
                fontSize: '42px',
                fontWeight: '700',
                color: COLORS.purple600,
                lineHeight: '1'
              }}>
                {COPY.simulation.withDeviation}
              </div>
              <div style={{
                fontSize: '16px',
                color: COLORS.textSecondary,
                fontWeight: '600'
              }}>
                de {COPY.simulation.totalMunicipalities.toLocaleString('pt-BR')}
              </div>
            </div>
            <div style={{
              fontSize: '13px',
              color: COLORS.purple600,
              fontWeight: '600',
              backgroundColor: COLORS.purple50,
              padding: '6px 10px',
              borderRadius: '6px',
              marginTop: '8px'
            }}>
              {COPY.simulation.percentWithDeviation}% com orçamento disponível acima da média
            </div>
          </div>

          {/* Card 2: Orçamento Total Disponível */}
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '12px',
            padding: '20px',
            border: `2px solid ${COLORS.borderPurple}`,
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 12px rgba(105, 65, 198, 0.08)'
          }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: COLORS.purple600,
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>💰</span>
              <span>ORÇAMENTO DISPONÍVEL</span>
            </div>
            <div style={{
              fontSize: '42px',
              fontWeight: '700',
              color: COLORS.textPrimary,
              lineHeight: '1',
              marginBottom: '8px'
            }}>
              {formatCurrency(COPY.simulation.availableTotal, true)}
            </div>
            <div style={{
              fontSize: '12px',
              color: COLORS.textSecondary,
              marginTop: '8px',
              lineHeight: '1.4'
            }}>
              Ainda não executado até agosto/2025 (restante até dezembro)
            </div>
          </div>

          {/* Card 3: OPORTUNIDADE (DESTAQUE) */}
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '12px',
            padding: '20px',
            border: `3px solid #10b981`,
            backdropFilter: 'blur(10px)',
            boxShadow: '0 6px 16px rgba(16, 185, 129, 0.25)',
            position: 'relative'
          }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: '#10b981',
              marginBottom: '12px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>💎</span>
              <span>OPORTUNIDADE IDENTIFICADA</span>
            </div>
            <div style={{
              fontSize: '42px',
              fontWeight: '700',
              color: '#10b981',
              lineHeight: '1',
              marginBottom: '12px'
            }}>
              {formatCurrency(COPY.simulation.opportunityValue, true)}
            </div>
            <div style={{
              fontSize: '12px',
              color: '#065f46',
              fontWeight: '600',
              lineHeight: '1.5'
            }}>
              Sobra acima da média nos {COPY.simulation.withDeviation} municípios com desvio
            </div>
          </div>

          {/* Card 4: Execução vs Esperado */}
          <div style={{
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '12px',
            padding: '20px',
            border: `2px solid ${COLORS.borderPurple}`,
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 12px rgba(105, 65, 198, 0.08)'
          }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: COLORS.purple600,
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>📊</span>
              <span>EXECUÇÃO ATÉ AGOSTO</span>
            </div>
            <div style={{
              fontSize: '28px',
              fontWeight: '700',
              color: COLORS.textPrimary,
              lineHeight: '1.2',
              marginBottom: '8px',
              display: 'flex',
              alignItems: 'baseline',
              gap: '8px'
            }}>
              <span style={{ color: COLORS.purple600 }}>{COPY.simulation.expectedExecutionRate}%</span>
              <span style={{ fontSize: '18px', color: COLORS.textSecondary }}>vs</span>
              <span style={{ color: '#dc2626' }}>{COPY.simulation.actualExecutionRateDeviation}%</span>
            </div>
            <div style={{
              fontSize: '11px',
              color: COLORS.textSecondary,
              marginBottom: '8px',
              lineHeight: '1.4'
            }}>
              Esperado (média 2022-2024) vs Real nos 850 municípios
            </div>
            <div style={{
              fontSize: '12px',
              color: '#dc2626',
              fontWeight: '600',
              lineHeight: '1.4'
            }}>
              {COPY.simulation.deviationPoints} pontos percentuais abaixo do padrão histórico
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
      <div style={{ marginBottom: '32px' }}>
        <div style={{
          marginBottom: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-end'
        }}>
          <div>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: COLORS.textPrimary,
              margin: 0,
              marginBottom: '4px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span>{COPY.sections.prioritarios.icon}</span>
              <span>{COPY.sections.prioritarios.title}</span>
            </h2>
            <p style={{
              fontSize: '14px',
              color: COLORS.textSecondary,
              margin: 0,
              maxWidth: '700px',
              lineHeight: '1.5'
            }}>
              {COPY.sections.prioritarios.subtitle}
            </p>
          </div>
          <div style={{
            textAlign: 'right'
          }}>
            <div style={{
              fontSize: '13px',
              fontWeight: '600',
              color: COLORS.purple600,
              marginBottom: '4px'
            }}>
              {formatCopyTemplate(COPY.sections.prioritarios.showing, {
                count: top3.length
              })}
            </div>
            <div style={{
              fontSize: '12px',
              color: COLORS.textSecondary
            }}>
              {formatCopyTemplate(COPY.sections.prioritarios.totalOpportunity, {
                value: formatCurrency(
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
                )
              })}
            </div>
          </div>
        </div>

        {/* Grid de Municípios */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px',
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

      {/* Gráfico de Comparação Top 10 */}
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
              <span>{COPY.sections.grafico.title}</span>
            </h2>
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              margin: 0
            }}>
              {COPY.sections.grafico.subtitle}
            </p>
          </div>

          {/* Seletor de Métrica */}
          <div style={{
            display: 'flex',
            gap: '8px',
            backgroundColor: '#ffffff',
            padding: '6px',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
            border: '1px solid #f5edff'
          }}>
            <button
              onClick={() => setComparisonMetric('extra')}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: comparisonMetric === 'extra' ? '#9755fe' : 'transparent',
                color: comparisonMetric === 'extra' ? '#ffffff' : '#6b7280',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              {COPY.sections.grafico.tabs.extra}
            </button>
            <button
              onClick={() => setComparisonMetric('executed')}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: comparisonMetric === 'executed' ? '#9755fe' : 'transparent',
                color: comparisonMetric === 'executed' ? '#ffffff' : '#6b7280',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              {COPY.sections.grafico.tabs.executed}
            </button>
            <button
              onClick={() => setComparisonMetric('deviation')}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                backgroundColor: comparisonMetric === 'deviation' ? '#9755fe' : 'transparent',
                color: comparisonMetric === 'deviation' ? '#ffffff' : '#6b7280',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              {COPY.sections.grafico.tabs.deviation}
            </button>
          </div>
        </div>

        <MunicipalityComparisonChart
          municipalities={comparisonData}
          metric={comparisonMetric}
          currentPeriod={currentPeriod}
          comparisonPeriod={comparisonPeriod}
        />
      </div>

      {/* Filtros Avançados */}
      <AdvancedFilters
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        comparisonMode={comparisonMode}
        onComparisonModeChange={setComparisonMode}
        selectedRegion={selectedRegion}
        onRegionChange={setSelectedRegion}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        chartType={chartType}
        onChartTypeChange={setChartType}
        currentPeriod={currentPeriod}
        onCurrentPeriodChange={setCurrentPeriod}
        comparisonPeriod={comparisonPeriod}
        onComparisonPeriodChange={setComparisonPeriod}
      />

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
            margin: 0
          }}>
            🏙️ Municípios ({filteredAndSortedMunicipalities.length})
          </h2>
          <div style={{
            fontSize: '14px',
            color: '#6b7280',
            fontWeight: '600'
          }}>
            Página {currentPage} de {totalPages}
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
  );
}

export default StrategicDashboard;
