import React from 'react';
import { ComparisonMode } from '../types/municipality';

interface AdvancedFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  comparisonMode: ComparisonMode;
  onComparisonModeChange: (mode: ComparisonMode) => void;
  selectedRegion: string;
  onRegionChange: (region: string) => void;
  sortBy: 'deviation' | 'extra' | 'executed';
  onSortByChange: (sort: 'deviation' | 'extra' | 'executed') => void;
  chartType: 'line' | 'bar';
  onChartTypeChange: (type: 'line' | 'bar') => void;
  currentPeriod?: number;
  onCurrentPeriodChange?: (year: number) => void;
  comparisonPeriod?: number;
  onComparisonPeriodChange?: (year: number) => void;
}

const AdvancedFilters: React.FC<AdvancedFiltersProps> = ({
  searchTerm,
  onSearchChange,
  comparisonMode,
  onComparisonModeChange,
  selectedRegion,
  onRegionChange,
  sortBy,
  onSortByChange,
  chartType,
  onChartTypeChange,
  currentPeriod,
  onCurrentPeriodChange,
  comparisonPeriod,
  onComparisonPeriodChange
}) => {
  const regions = ['Todos', 'Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];

  // Anos eleitorais (eleições municipais ocorrem a cada 4 anos)
  const electoralYears = [2024, 2020, 2016, 2012, 2008, 2004, 2000];
  const allYears = [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012];

  const comparisonModes = [
    { value: 'avg-electoral', label: '📊 Média Eleitorais', icon: '📊' },
    { value: 'last-electoral', label: '🗳️ Último Eleitoral', icon: '🗳️' },
    { value: 'avg-all', label: '📈 Média Geral', icon: '📈' },
    { value: 'previous-year', label: '📅 Ano Anterior', icon: '📅' }
  ];

  const sortOptions = [
    { value: 'deviation', label: 'Maior Desvio' },
    { value: 'extra', label: 'Maior Sobra' },
    { value: 'executed', label: 'Maior Execução' }
  ];

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff',
      marginBottom: '24px'
    }}>
      <h3 style={{
        fontSize: '16px',
        fontWeight: '700',
        color: '#2e3138',
        marginBottom: '20px',
        display: 'flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        🔍 Filtros Avançados
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '16px'
      }}>
        {/* Busca */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Buscar Município
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Digite o nome..."
            style={{
              width: '100%',
              padding: '10px 14px',
              fontSize: '14px',
              border: '2px solid #e1cdfe',
              borderRadius: '8px',
              backgroundColor: '#f9f4ff',
              color: '#2e3138',
              outline: 'none',
              transition: 'all 0.2s'
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = '#9755fe';
              e.currentTarget.style.backgroundColor = '#ffffff';
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = '#e1cdfe';
              e.currentTarget.style.backgroundColor = '#f9f4ff';
            }}
          />
        </div>

        {/* Modo de Comparação */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Comparar com
          </label>
          <select
            value={comparisonMode}
            onChange={(e) => onComparisonModeChange(e.target.value as ComparisonMode)}
            style={{
              width: '100%',
              padding: '10px 14px',
              fontSize: '14px',
              border: '2px solid #e1cdfe',
              borderRadius: '8px',
              backgroundColor: '#f9f4ff',
              color: '#2e3138',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            {comparisonModes.map(mode => (
              <option key={mode.value} value={mode.value}>
                {mode.label}
              </option>
            ))}
          </select>
        </div>

        {/* Região */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Região
          </label>
          <select
            value={selectedRegion}
            onChange={(e) => onRegionChange(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px',
              fontSize: '14px',
              border: '2px solid #e1cdfe',
              borderRadius: '8px',
              backgroundColor: '#f9f4ff',
              color: '#2e3138',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            {regions.map(region => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
        </div>

        {/* Ordenação */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Ordenar por
          </label>
          <select
            value={sortBy}
            onChange={(e) => onSortByChange(e.target.value as any)}
            style={{
              width: '100%',
              padding: '10px 14px',
              fontSize: '14px',
              border: '2px solid #e1cdfe',
              borderRadius: '8px',
              backgroundColor: '#f9f4ff',
              color: '#2e3138',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            {sortOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Tipo de Gráfico */}
        <div>
          <label style={{
            display: 'block',
            fontSize: '12px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '8px',
            textTransform: 'uppercase'
          }}>
            Tipo de Gráfico
          </label>
          <div style={{
            display: 'flex',
            gap: '8px'
          }}>
            <button
              onClick={() => onChartTypeChange('line')}
              style={{
                flex: 1,
                padding: '10px',
                fontSize: '14px',
                fontWeight: '600',
                border: '2px solid',
                borderColor: chartType === 'line' ? '#9755fe' : '#e1cdfe',
                borderRadius: '8px',
                backgroundColor: chartType === 'line' ? '#f9f4ff' : '#ffffff',
                color: chartType === 'line' ? '#9755fe' : '#6b7280',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              📈
            </button>
            <button
              onClick={() => onChartTypeChange('bar')}
              style={{
                flex: 1,
                padding: '10px',
                fontSize: '14px',
                fontWeight: '600',
                border: '2px solid',
                borderColor: chartType === 'bar' ? '#9755fe' : '#e1cdfe',
                borderRadius: '8px',
                backgroundColor: chartType === 'bar' ? '#f9f4ff' : '#ffffff',
                color: chartType === 'bar' ? '#9755fe' : '#6b7280',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              📊
            </button>
          </div>
        </div>
      </div>

      {/* Comparação de Períodos */}
      {onCurrentPeriodChange && onComparisonPeriodChange && (
        <div style={{
          borderTop: '1px solid #e1cdfe',
          paddingTop: '16px'
        }}>
          <h4 style={{
            fontSize: '14px',
            fontWeight: '700',
            color: '#2e3138',
            marginBottom: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            📅 Comparação Temporal
          </h4>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            {/* Período Atual */}
            <div>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#5219a1',
                marginBottom: '8px',
                textTransform: 'uppercase'
              }}>
                Período Atual
              </label>
              <select
                value={currentPeriod}
                onChange={(e) => onCurrentPeriodChange(parseInt(e.target.value))}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  fontSize: '14px',
                  border: '2px solid #e1cdfe',
                  borderRadius: '8px',
                  backgroundColor: '#f9f4ff',
                  color: '#2e3138',
                  cursor: 'pointer',
                  outline: 'none'
                }}
              >
                {allYears.map(year => (
                  <option key={year} value={year}>
                    {year} {electoralYears.includes(year) ? '🗳️ (Eleitoral)' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Período de Comparação */}
            <div>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: '600',
                color: '#5219a1',
                marginBottom: '8px',
                textTransform: 'uppercase'
              }}>
                Comparar com
              </label>
              <select
                value={comparisonPeriod}
                onChange={(e) => onComparisonPeriodChange(parseInt(e.target.value))}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  fontSize: '14px',
                  border: '2px solid #e1cdfe',
                  borderRadius: '8px',
                  backgroundColor: '#f9f4ff',
                  color: '#2e3138',
                  cursor: 'pointer',
                  outline: 'none'
                }}
              >
                {electoralYears.map(year => (
                  <option key={year} value={year}>
                    {year} 🗳️ (Eleitoral)
                  </option>
                ))}
              </select>
            </div>

            {/* Info */}
            <div style={{
              gridColumn: '1 / -1',
              padding: '12px',
              backgroundColor: '#f0f9ff',
              borderRadius: '8px',
              border: '1px solid #bae6fd',
              fontSize: '12px',
              color: '#0369a1',
              lineHeight: '1.5'
            }}>
              💡 <strong>Dica:</strong> Compare o ano atual ({currentPeriod}) com anos eleitorais anteriores
              para identificar padrões de subexecução em períodos eleitorais.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedFilters;
