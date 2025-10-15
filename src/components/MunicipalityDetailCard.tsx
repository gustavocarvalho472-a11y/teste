import React from 'react';
import { MunicipalityBudget, ComparisonMode } from '../types/municipality';
import { formatCurrency } from '../utils';

interface MunicipalityDetailCardProps {
  municipality: MunicipalityBudget;
  mode: ComparisonMode;
  onSelect: (id: string) => void;
}

const MunicipalityDetailCard: React.FC<MunicipalityDetailCardProps> = ({
  municipality,
  mode,
  onSelect
}) => {
  const getComparison = () => {
    switch (mode) {
      case 'avg-electoral': return municipality.comparison.avgElectoral;
      case 'last-electoral': return municipality.comparison.lastElectoral;
      case 'avg-all': return municipality.comparison.avgAll;
      case 'previous-year': return municipality.comparison.previousYear;
    }
  };

  const comparison = getComparison();

  // Garantir valores válidos
  if (!comparison || comparison.executedAmount === undefined || comparison.referenceAmount === undefined) {
    return null;
  }

  const extra = comparison.referenceAmount - comparison.executedAmount;
  const percentExecuted = (comparison.executedAmount / comparison.referenceAmount) * 100;

  return (
    <div
      onClick={() => onSelect(municipality.id)}
      style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
        border: '2px solid #f5edff',
        cursor: 'pointer',
        transition: 'all 0.3s'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 8px 20px rgba(151, 85, 254, 0.2)';
        e.currentTarget.style.borderColor = '#9755fe';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
        e.currentTarget.style.borderColor = '#f5edff';
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #f5edff'
      }}>
        <div>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#2e3138',
            margin: 0,
            marginBottom: '6px'
          }}>
            {municipality.name}
          </h3>
          <div style={{
            fontSize: '13px',
            color: '#6b7280'
          }}>
            {municipality.state} · {municipality.region}
          </div>
        </div>
        <div style={{
          padding: '6px 12px',
          backgroundColor: '#f9f4ff',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: '600',
          color: '#5219a1'
        }}>
          {comparison.severity === 'critical' ? '🔴 Crítico' :
           comparison.severity === 'high' ? '🟠 Alto' :
           comparison.severity === 'moderate' ? '🟡 Moderado' : '🟢 Leve'}
        </div>
      </div>

      {/* Métricas principais */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <div style={{
          padding: '12px',
          backgroundColor: '#f0fdf4',
          borderRadius: '8px',
          border: '1px solid #86efac'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#065f46',
            marginBottom: '4px',
            textTransform: 'uppercase'
          }}>
            Sobra Disponível
          </div>
          <div style={{
            fontSize: '20px',
            fontWeight: '700',
            color: '#059669'
          }}>
            {formatCurrency(extra, true)}
          </div>
        </div>

        <div style={{
          padding: '12px',
          backgroundColor: '#f9f4ff',
          borderRadius: '8px',
          border: '1px solid #d1b3ff'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '4px',
            textTransform: 'uppercase'
          }}>
            % Executado
          </div>
          <div style={{
            fontSize: '20px',
            fontWeight: '700',
            color: '#9755fe'
          }}>
            {percentExecuted.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Barra de progresso */}
      <div style={{
        marginBottom: '12px'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '6px'
        }}>
          <span style={{
            fontSize: '12px',
            color: '#6b7280',
            fontWeight: '600'
          }}>
            Execução vs Referência
          </span>
          <span style={{
            fontSize: '12px',
            fontWeight: '700',
            color: comparison.percentageDeviation < 0 ? '#059669' : '#ef4444'
          }}>
            {comparison.percentageDeviation.toFixed(1)}%
          </span>
        </div>
        <div style={{
          width: '100%',
          height: '8px',
          backgroundColor: '#f3f4f6',
          borderRadius: '4px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${Math.min(percentExecuted, 100)}%`,
            height: '100%',
            backgroundColor: percentExecuted < 80 ? '#10b981' : percentExecuted < 95 ? '#f59e0b' : '#9755fe',
            transition: 'width 0.5s'
          }} />
        </div>
      </div>

      {/* Footer com call to action */}
      <div style={{
        fontSize: '12px',
        color: '#9755fe',
        fontWeight: '600',
        textAlign: 'center',
        paddingTop: '8px'
      }}>
        Clique para análise detalhada →
      </div>
    </div>
  );
};

export default MunicipalityDetailCard;
