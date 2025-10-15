import React, { useState, useMemo } from 'react';
import { municipalityBudgetData } from './mockData/municipalityData';
import { ComparisonMode } from './types/municipality';
import MunicipalityDetailCard from './components/MunicipalityDetailCard';
import MunicipalityTimeSeriesChart from './components/MunicipalityTimeSeriesChart';
import MunicipalityComparisonChart from './components/MunicipalityComparisonChart';
import AdvancedFilters from './components/AdvancedFilters';

function MunicipalityDetailDashboard() {
  const [selectedMunicipalityId, setSelectedMunicipalityId] = useState<string | null>(null);
  const [comparisonMode, setComparisonMode] = useState<ComparisonMode>('avg-electoral');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('Todos');
  const [sortBy, setSortBy] = useState<'deviation' | 'extra' | 'executed'>('extra');
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');
  const [comparisonMetric, setComparisonMetric] = useState<'executed' | 'deviation' | 'extra'>('extra');
  const [currentPeriod, setCurrentPeriod] = useState<number>(2024);
  const [comparisonPeriod, setComparisonPeriod] = useState<number>(2020);

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

  // Município selecionado
  const selectedMunicipality = selectedMunicipalityId
    ? municipalityBudgetData.find(m => m.id === selectedMunicipalityId)
    : null;

  // Dados para série temporal (usando dados históricos reais)
  const timeSeriesData = useMemo(() => {
    if (!selectedMunicipality || !selectedMunicipality.history) return [];

    // Usar dados históricos reais do município
    return selectedMunicipality.history.map(yearData => {
      const reference = yearData.totalBudget;
      const executed = yearData.executed;
      const deviation = ((executed / reference) - 1) * 100;

      return {
        year: yearData.year,
        executed: executed,
        reference: reference,
        deviation: deviation
      };
    });
  }, [selectedMunicipality]);

  // Calcular valor do ano de comparação eleitoral (usando dados históricos reais)
  const comparisonYearValue = useMemo(() => {
    if (!selectedMunicipality || !comparisonPeriod || !selectedMunicipality.history) return undefined;

    // Buscar o valor executado no ano de comparação selecionado
    const comparisonYearData = selectedMunicipality.history.find(h => h.year === comparisonPeriod);

    if (!comparisonYearData) {
      // Se não tiver dados históricos para esse ano, estimar baseado no padrão do município
      // Usa taxa de execução média de anos eleitorais (2020, 2022, 2024)
      const electoralYears = selectedMunicipality.history.filter(h => h.isElectionYear);
      if (electoralYears.length > 0) {
        const avgExecutionRate = electoralYears.reduce((sum, y) => sum + y.executionRate, 0) / electoralYears.length;
        // Estimar baseado no orçamento atual
        const currentYear = selectedMunicipality.history.find(h => h.year === 2024);
        if (currentYear) {
          return currentYear.totalBudget * (avgExecutionRate / 100);
        }
      }
      return undefined;
    }

    return comparisonYearData.executed;
  }, [selectedMunicipality, comparisonPeriod]);

  // Dados para comparação entre municípios
  const comparisonData = useMemo(() => {
    return filteredAndSortedMunicipalities.map(m => {
      const comp = m.comparison[
        comparisonMode === 'avg-electoral' ? 'avgElectoral' :
        comparisonMode === 'last-electoral' ? 'lastElectoral' :
        comparisonMode === 'avg-all' ? 'avgAll' : 'previousYear'
      ];

      // Buscar valor executado no período de comparação (ano eleitoral)
      let comparisonExecuted = 0;
      if (m.history && comparisonPeriod) {
        const comparisonYearData = m.history.find(h => h.year === comparisonPeriod);
        if (comparisonYearData) {
          comparisonExecuted = comparisonYearData.executed;
        } else {
          // Estimar baseado na média de anos eleitorais
          const electoralYears = m.history.filter(h => h.isElectionYear);
          if (electoralYears.length > 0) {
            const avgExecutionRate = electoralYears.reduce((sum, y) => sum + y.executionRate, 0) / electoralYears.length;
            const currentYear = m.history.find(h => h.year === currentPeriod);
            if (currentYear) {
              comparisonExecuted = currentYear.totalBudget * (avgExecutionRate / 100);
            }
          }
        }
      }

      return {
        name: m.name,
        executed: comp.executedAmount,
        reference: comp.referenceAmount,
        deviation: comp.percentageDeviation,
        comparisonExecuted
      };
    });
  }, [filteredAndSortedMunicipalities, comparisonMode, comparisonPeriod, currentPeriod]);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#f9f4ff',
      padding: '32px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    }}>
      {/* Hero Section */}
      <div style={{
        backgroundColor: '#2e3138',
        borderRadius: '16px',
        padding: '40px',
        marginBottom: '32px',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.15)',
        background: 'linear-gradient(135deg, #2e3138 0%, #5219a1 100%)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#d1b3ff',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '8px'
          }}>
            Análise Detalhada Municipal
          </div>
          <h1 style={{
            fontSize: '36px',
            fontWeight: '700',
            color: '#ffffff',
            margin: 0,
            lineHeight: '1.2',
            marginBottom: '12px'
          }}>
            🏛️ Drill-Down por Município
          </h1>
          <p style={{
            fontSize: '16px',
            color: '#ba90fc',
            margin: 0
          }}>
            Séries Temporais · Comparações Multi-Município · Análise Individual Profunda
          </p>
        </div>
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

      {/* Estatísticas Gerais */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          border: '2px solid #f5edff'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Municípios Analisados
          </div>
          <div style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#2e3138'
          }}>
            {filteredAndSortedMunicipalities.length}
          </div>
        </div>

        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          border: '2px solid #d1fae5'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#065f46',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Sobra Total Disponível
          </div>
          <div style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#059669'
          }}>
            {new Intl.NumberFormat('pt-BR', {
              style: 'currency',
              currency: 'BRL',
              notation: 'compact',
              maximumFractionDigits: 1
            }).format(
              filteredAndSortedMunicipalities.reduce((sum, m) => {
                const comp = m.comparison[
                  comparisonMode === 'avg-electoral' ? 'avgElectoral' :
                  comparisonMode === 'last-electoral' ? 'lastElectoral' :
                  comparisonMode === 'avg-all' ? 'avgAll' : 'previousYear'
                ];
                return sum + (comp.referenceAmount - comp.executedAmount);
              }, 0)
            )}
          </div>
        </div>

        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          border: '2px solid #fef3c7'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#92400e',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Desvio Médio
          </div>
          <div style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#b45309'
          }}>
            {(filteredAndSortedMunicipalities.reduce((sum, m) => {
              const comp = m.comparison[
                comparisonMode === 'avg-electoral' ? 'avgElectoral' :
                comparisonMode === 'last-electoral' ? 'lastElectoral' :
                comparisonMode === 'avg-all' ? 'avgAll' : 'previousYear'
              ];
              return sum + comp.percentageDeviation;
            }, 0) / filteredAndSortedMunicipalities.length).toFixed(1)}%
          </div>
        </div>

        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          border: '2px solid #fee2e2'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#991b1b',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Casos Críticos
          </div>
          <div style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#dc2626'
          }}>
            {filteredAndSortedMunicipalities.filter(m => {
              const comp = m.comparison[
                comparisonMode === 'avg-electoral' ? 'avgElectoral' :
                comparisonMode === 'last-electoral' ? 'lastElectoral' :
                comparisonMode === 'avg-all' ? 'avgAll' : 'previousYear'
              ];
              return comp.severity === 'critical';
            }).length}
          </div>
        </div>
      </div>

      {/* Gráfico de Comparação */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          padding: '16px 24px',
          marginBottom: '16px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          border: '1px solid #f5edff',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <span style={{
            fontSize: '14px',
            fontWeight: '600',
            color: '#5219a1'
          }}>
            Métrica de Comparação:
          </span>
          <div style={{ display: 'flex', gap: '8px' }}>
            {[
              { value: 'extra', label: 'Sobra Disponível' },
              { value: 'deviation', label: 'Desvio %' },
              { value: 'executed', label: 'Valor Executado' }
            ].map(option => (
              <button
                key={option.value}
                onClick={() => setComparisonMetric(option.value as any)}
                style={{
                  padding: '8px 16px',
                  fontSize: '13px',
                  fontWeight: '600',
                  border: '2px solid',
                  borderColor: comparisonMetric === option.value ? '#9755fe' : '#e1cdfe',
                  borderRadius: '8px',
                  backgroundColor: comparisonMetric === option.value ? '#f9f4ff' : '#ffffff',
                  color: comparisonMetric === option.value ? '#9755fe' : '#6b7280',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <MunicipalityComparisonChart
          municipalities={comparisonData}
          metric={comparisonMetric}
          currentPeriod={currentPeriod}
          comparisonPeriod={comparisonPeriod}
        />
      </div>

      {/* Série Temporal (se houver município selecionado) */}
      {selectedMunicipality && (
        <div style={{ marginBottom: '32px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '16px'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: '700',
              color: '#2e3138',
              margin: 0
            }}>
              📊 Análise Temporal: {selectedMunicipality.name}
            </h2>
            <button
              onClick={() => setSelectedMunicipalityId(null)}
              style={{
                padding: '8px 16px',
                fontSize: '13px',
                fontWeight: '600',
                border: '2px solid #ef4444',
                borderRadius: '8px',
                backgroundColor: '#ffffff',
                color: '#ef4444',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              ✕ Fechar
            </button>
          </div>
          <MunicipalityTimeSeriesChart
            municipalityName={selectedMunicipality.name}
            data={timeSeriesData}
            chartType={chartType}
            comparisonYear={comparisonPeriod}
            comparisonValue={comparisonYearValue}
          />
        </div>
      )}

      {/* Grid de Municípios */}
      <div>
        <h2 style={{
          fontSize: '20px',
          fontWeight: '700',
          color: '#2e3138',
          marginBottom: '20px'
        }}>
          🏙️ Municípios ({filteredAndSortedMunicipalities.length})
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '20px'
        }}>
          {filteredAndSortedMunicipalities.map(municipality => (
            <MunicipalityDetailCard
              key={municipality.id}
              municipality={municipality}
              mode={comparisonMode}
              onSelect={setSelectedMunicipalityId}
            />
          ))}
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
          Dashboard de Análise Municipal Detalhada · Drill-Down & Séries Temporais
        </p>
      </div>
    </div>
  );
}

export default MunicipalityDetailDashboard;
