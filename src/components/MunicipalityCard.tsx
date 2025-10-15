import React from 'react';
import { MunicipalityBudget, ComparisonMode } from '../types/municipality';
import { formatCurrency } from '../utils';

interface MunicipalityCardProps {
  municipality: MunicipalityBudget;
  comparisonMode: ComparisonMode;
  rank?: number;
}

const MunicipalityCard: React.FC<MunicipalityCardProps> = ({
  municipality,
  comparisonMode,
  rank
}) => {
  const getComparison = () => {
    switch (comparisonMode) {
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

  const extraAvailable = comparison.referenceAmount - comparison.executedAmount;
  const percentageDiff = comparison.percentageDeviation;
  const difference = comparison.referenceAmount - comparison.executedAmount;

  const severityColor = comparison.severity === 'critical' ? '#ef4444' :
                       comparison.severity === 'moderate' ? '#f59e0b' : '#10b981';

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: `3px solid ${severityColor}`,
      position: 'relative',
      transition: 'all 0.3s'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-6px)';
      e.currentTarget.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.15)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
    }}
    >
      {/* Badge de Ranking */}
      {rank && (
        <div style={{
          position: 'absolute',
          top: '-16px',
          left: '20px',
          backgroundColor: severityColor,
          color: '#ffffff',
          padding: '8px 16px',
          borderRadius: '20px',
          fontSize: '16px',
          fontWeight: '700',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          {rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `#${rank}`}
        </div>
      )}

      {/* Header */}
      <div style={{
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #f5edff'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '8px'
        }}>
          <div>
            <h3 style={{
              fontSize: '22px',
              fontWeight: '700',
              color: '#2e3138',
              margin: '0 0 4px 0'
            }}>
              {municipality.name}
            </h3>
            <div style={{
              fontSize: '13px',
              color: '#6b7280',
              fontWeight: '500'
            }}>
              {municipality.state} · {municipality.region}
            </div>
          </div>
          <div style={{
            padding: '6px 12px',
            backgroundColor: comparison.severity === 'critical' ? '#fee2e2' :
                           comparison.severity === 'moderate' ? '#fef3c7' : '#d1fae5',
            borderRadius: '6px',
            fontSize: '11px',
            fontWeight: '700',
            color: severityColor,
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            {comparison.severity === 'critical' ? '🔴 Crítico' :
             comparison.severity === 'moderate' ? '🟡 Moderado' : '🟢 Normal'}
          </div>
        </div>
      </div>

      {/* Métricas Principais */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        marginBottom: '16px'
      }}>
        <div style={{
          padding: '16px',
          backgroundColor: '#fee2e2',
          borderRadius: '8px',
          border: '1px solid #fca5a5'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#991b1b',
            marginBottom: '6px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            💰 Dinheiro Sobrando
          </div>
          <div style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#dc2626',
            marginBottom: '4px'
          }}>
            {formatCurrency(extraAvailable, true)}
          </div>
          <div style={{
            fontSize: '11px',
            color: '#991b1b'
          }}>
            vs Referência
          </div>
        </div>

        <div style={{
          padding: '16px',
          backgroundColor: '#f9f4ff',
          borderRadius: '8px',
          border: '1px solid #d1b3ff'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#5219a1',
            marginBottom: '6px'
          }}>
            📊 % Executado
          </div>
          <div style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#3f127d',
            marginBottom: '4px'
          }}>
            {municipality.executionRate.toFixed(1)}%
          </div>
          <div style={{
            fontSize: '11px',
            color: '#5219a1'
          }}>
            de R$ {(municipality.totalBudget / 1000000000).toFixed(1)}bi
          </div>
        </div>
      </div>

      {/* Comparação Detalhada */}
      <div style={{
        padding: '16px',
        backgroundColor: '#f9f4ff',
        borderRadius: '8px',
        marginBottom: '16px'
      }}>
        <div style={{
          fontSize: '12px',
          fontWeight: '600',
          color: '#5219a1',
          marginBottom: '12px'
        }}>
          Comparação vs Referência
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '8px',
          fontSize: '13px'
        }}>
          <span style={{ color: '#6b7280' }}>Referência:</span>
          <span style={{ fontWeight: '600', color: '#2e3138' }}>
            {formatCurrency(comparison.referenceAmount, true)}
          </span>
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '8px',
          fontSize: '13px'
        }}>
          <span style={{ color: '#6b7280' }}>Executado:</span>
          <span style={{ fontWeight: '600', color: '#2e3138' }}>
            {formatCurrency(comparison.executedAmount, true)}
          </span>
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '13px',
          paddingTop: '8px',
          borderTop: '1px solid #e1cdfe'
        }}>
          <span style={{ color: '#6b7280', fontWeight: '600' }}>Desvio:</span>
          <span style={{
            fontWeight: '700',
            color: percentageDiff < 0 ? '#10b981' : '#ef4444',
            fontSize: '14px'
          }}>
            {percentageDiff.toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Contexto */}
      {municipality.events.length > 0 && (
        <div style={{
          display: 'flex',
          gap: '6px',
          flexWrap: 'wrap',
          marginBottom: '12px'
        }}>
          {municipality.events.map((event, i) => (
            <span
              key={i}
              style={{
                fontSize: '11px',
                padding: '4px 8px',
                backgroundColor: '#e1cdfe',
                borderRadius: '4px',
                color: '#5219a1',
                fontWeight: '500'
              }}
            >
              {event}
            </span>
          ))}
        </div>
      )}

      {/* Análise */}
      <div style={{
        padding: '12px',
        backgroundColor: percentageDiff < 0 ? '#fee2e2' : '#d1fae5',
        borderRadius: '6px',
        border: `1px solid ${percentageDiff < 0 ? '#fca5a5' : '#86efac'}`
      }}>
        <div style={{
          fontSize: '11px',
          fontWeight: '600',
          color: percentageDiff < 0 ? '#991b1b' : '#065f46',
          marginBottom: '4px'
        }}>
          💡 Análise Rápida
        </div>
        <div style={{
          fontSize: '12px',
          color: percentageDiff < 0 ? '#991b1b' : '#065f46',
          lineHeight: '1.5'
        }}>
          {comparison.severity === 'critical' && percentageDiff < 0 &&
            `Subexecução crítica de ${Math.abs(percentageDiff).toFixed(1)}%. Há ${formatCurrency(extraAvailable, true)} a mais sobrando que o esperado.`
          }
          {comparison.severity === 'moderate' && percentageDiff < 0 &&
            `Subexecução moderada de ${Math.abs(percentageDiff).toFixed(1)}%. Recurso disponível acima do padrão histórico.`
          }
          {comparison.severity === 'normal' &&
            `Execução dentro da normalidade esperada para o período.`
          }
        </div>
      </div>
    </div>
  );
};

export default MunicipalityCard;
