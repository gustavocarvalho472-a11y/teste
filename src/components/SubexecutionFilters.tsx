import React from 'react';
import { ComparisonMode, EntityType } from '../types/municipality';

interface SubexecutionFiltersProps {
  comparisonMode: ComparisonMode;
  onComparisonModeChange: (mode: ComparisonMode) => void;
  entityType: EntityType | 'all';
  onEntityTypeChange: (type: EntityType | 'all') => void;
  totalCount: number;
  anomalyCount: number;
}

const SubexecutionFilters: React.FC<SubexecutionFiltersProps> = ({
  comparisonMode,
  onComparisonModeChange,
  entityType,
  onEntityTypeChange,
  totalCount,
  anomalyCount
}) => {
  const comparisonModes = [
    { value: 'avg-electoral' as ComparisonMode, label: '📊 Média Eleitorais', desc: 'Últimos períodos eleitorais' },
    { value: 'last-electoral' as ComparisonMode, label: '🗳️ Último Eleitoral', desc: '2022' },
    { value: 'avg-all' as ComparisonMode, label: '📈 Média Geral', desc: 'Todos os anos' },
    { value: 'previous-year' as ComparisonMode, label: '📅 Ano Anterior', desc: '2023' }
  ];

  const entityTypes = [
    { value: 'all' as const, label: 'Todos', icon: '🌎' },
    { value: 'municipality' as EntityType, label: 'Municípios', icon: '🏙️' },
    { value: 'state' as EntityType, label: 'Estados', icon: '🗺️' },
    { value: 'region' as EntityType, label: 'Regiões', icon: '📍' }
  ];

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      marginBottom: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: '24px',
        flexWrap: 'wrap'
      }}>
        {/* Modo de Comparação */}
        <div style={{ flex: '1 1 400px' }}>
          <label style={{
            display: 'block',
            fontSize: '13px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '12px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Comparar com:
          </label>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '8px'
          }}>
            {comparisonModes.map(mode => (
              <button
                key={mode.value}
                onClick={() => onComparisonModeChange(mode.value)}
                style={{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  border: comparisonMode === mode.value ? '2px solid #9755fe' : '1px solid #e1cdfe',
                  backgroundColor: comparisonMode === mode.value ? '#f5edff' : '#ffffff',
                  color: comparisonMode === mode.value ? '#3f127d' : '#6b7280',
                  fontSize: '13px',
                  fontWeight: comparisonMode === mode.value ? '600' : '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => {
                  if (comparisonMode !== mode.value) {
                    e.currentTarget.style.backgroundColor = '#f9f4ff';
                    e.currentTarget.style.borderColor = '#d1b3ff';
                  }
                }}
                onMouseLeave={(e) => {
                  if (comparisonMode !== mode.value) {
                    e.currentTarget.style.backgroundColor = '#ffffff';
                    e.currentTarget.style.borderColor = '#e1cdfe';
                  }
                }}
              >
                <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                  {mode.label}
                </div>
                <div style={{ fontSize: '11px', opacity: 0.8 }}>
                  {mode.desc}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Tipo de Entidade */}
        <div style={{ flex: '0 0 auto' }}>
          <label style={{
            display: 'block',
            fontSize: '13px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '12px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Filtrar por:
          </label>
          <div style={{
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap'
          }}>
            {entityTypes.map(type => (
              <button
                key={type.value}
                onClick={() => onEntityTypeChange(type.value)}
                style={{
                  padding: '10px 16px',
                  borderRadius: '8px',
                  border: entityType === type.value ? '2px solid #9755fe' : '1px solid #e1cdfe',
                  backgroundColor: entityType === type.value ? '#f5edff' : '#ffffff',
                  color: entityType === type.value ? '#3f127d' : '#6b7280',
                  fontSize: '13px',
                  fontWeight: entityType === type.value ? '600' : '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
                onMouseEnter={(e) => {
                  if (entityType !== type.value) {
                    e.currentTarget.style.backgroundColor = '#f9f4ff';
                    e.currentTarget.style.borderColor = '#d1b3ff';
                  }
                }}
                onMouseLeave={(e) => {
                  if (entityType !== type.value) {
                    e.currentTarget.style.backgroundColor = '#ffffff';
                    e.currentTarget.style.borderColor = '#e1cdfe';
                  }
                }}
              >
                <span>{type.icon}</span>
                <span>{type.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Contador */}
        <div style={{
          flex: '0 0 auto',
          display: 'flex',
          gap: '12px',
          alignItems: 'flex-end'
        }}>
          <div style={{
            padding: '12px 16px',
            backgroundColor: '#f9f4ff',
            borderRadius: '8px',
            textAlign: 'center',
            minWidth: '100px'
          }}>
            <div style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#3f127d',
              lineHeight: '1'
            }}>
              {anomalyCount}
            </div>
            <div style={{
              fontSize: '11px',
              color: '#5219a1',
              marginTop: '4px',
              fontWeight: '600'
            }}>
              Com Anomalia
            </div>
          </div>
          <div style={{
            padding: '12px 16px',
            backgroundColor: '#e1cdfe',
            borderRadius: '8px',
            textAlign: 'center',
            minWidth: '100px'
          }}>
            <div style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#3f127d',
              lineHeight: '1'
            }}>
              {totalCount}
            </div>
            <div style={{
              fontSize: '11px',
              color: '#5219a1',
              marginTop: '4px',
              fontWeight: '600'
            }}>
              Total
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubexecutionFilters;
