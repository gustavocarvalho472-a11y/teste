import React from 'react';
import { YearlyAnomaly } from '../utils/anomalyDetection';
import { getSeverityColor, getSeverityIcon } from '../utils/anomalyDetection';
import { formatCurrency } from '../utils';

interface AnomalyCardProps {
  anomaly: YearlyAnomaly;
  rank?: number;
}

const AnomalyCard: React.FC<AnomalyCardProps> = ({ anomaly, rank }) => {
  const isPositive = anomaly.zScore > 0;
  const color = getSeverityColor(anomaly.severity);

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: `2px solid ${color}`,
      position: 'relative',
      transition: 'all 0.3s'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
      e.currentTarget.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.12)';
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
          top: '-12px',
          right: '20px',
          backgroundColor: color,
          color: '#ffffff',
          padding: '6px 12px',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: '700',
          boxShadow: '0 2px 6px rgba(0, 0, 0, 0.2)'
        }}>
          #{rank}
        </div>
      )}

      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <div style={{
          fontSize: '32px',
          lineHeight: '1'
        }}>
          {getSeverityIcon(anomaly.severity)}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '600',
            color: color,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '4px'
          }}>
            {anomaly.severity === 'critical' ? 'ANOMALIA CRÍTICA' :
             anomaly.severity === 'moderate' ? 'ANOMALIA MODERADA' : 'COMPORTAMENTO NORMAL'}
          </div>
          <div style={{
            fontSize: '20px',
            fontWeight: '700',
            color: '#2e3138'
          }}>
            {anomaly.year} - {anomaly.governmentContext}
          </div>
        </div>
      </div>

      {/* Métricas Principais */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        marginBottom: '16px',
        padding: '16px',
        backgroundColor: '#f9f4ff',
        borderRadius: '8px'
      }}>
        <div>
          <div style={{
            fontSize: '12px',
            color: '#5219a1',
            fontWeight: '600',
            marginBottom: '4px'
          }}>
            Desvio da Média
          </div>
          <div style={{
            fontSize: '24px',
            fontWeight: '700',
            color: isPositive ? '#10b981' : '#ef4444'
          }}>
            {isPositive ? '+' : ''}{anomaly.percentageDeviation.toFixed(1)}%
          </div>
        </div>
        <div>
          <div style={{
            fontSize: '12px',
            color: '#5219a1',
            fontWeight: '600',
            marginBottom: '4px'
          }}>
            Z-Score
          </div>
          <div style={{
            fontSize: '24px',
            fontWeight: '700',
            color: color
          }}>
            {anomaly.zScore.toFixed(2)}σ
          </div>
        </div>
      </div>

      {/* Valores */}
      <div style={{
        marginBottom: '16px'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '8px'
        }}>
          <span style={{ fontSize: '13px', color: '#6b7280' }}>Valor Executado:</span>
          <span style={{ fontSize: '14px', fontWeight: '600', color: '#2e3138' }}>
            {formatCurrency(anomaly.value, true)}
          </span>
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '8px'
        }}>
          <span style={{ fontSize: '13px', color: '#6b7280' }}>Média Histórica:</span>
          <span style={{ fontSize: '14px', fontWeight: '600', color: '#2e3138' }}>
            {formatCurrency(anomaly.mean, true)}
          </span>
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between'
        }}>
          <span style={{ fontSize: '13px', color: '#6b7280' }}>Diferença:</span>
          <span style={{
            fontSize: '14px',
            fontWeight: '700',
            color: isPositive ? '#10b981' : '#ef4444'
          }}>
            {isPositive ? '+' : ''}{formatCurrency(anomaly.value - anomaly.mean, true)}
          </span>
        </div>
      </div>

      {/* Contexto e Eventos */}
      {anomaly.events.length > 0 && (
        <div style={{
          padding: '12px',
          backgroundColor: '#e1cdfe',
          borderRadius: '6px',
          marginBottom: '12px'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#3f127d',
            marginBottom: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            📍 Contexto do Ano
          </div>
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px'
          }}>
            {anomaly.events.map((event, i) => (
              <span
                key={i}
                style={{
                  fontSize: '11px',
                  padding: '4px 8px',
                  backgroundColor: '#ffffff',
                  borderRadius: '4px',
                  color: '#5219a1',
                  fontWeight: '500'
                }}
              >
                {event}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Análise Automática */}
      <div style={{
        padding: '12px',
        backgroundColor: isPositive ? '#d1fae5' : '#fee2e2',
        borderRadius: '6px',
        border: `1px solid ${isPositive ? '#86efac' : '#fca5a5'}`
      }}>
        <div style={{
          fontSize: '11px',
          fontWeight: '600',
          color: isPositive ? '#065f46' : '#991b1b',
          marginBottom: '4px'
        }}>
          💡 Análise
        </div>
        <div style={{
          fontSize: '12px',
          color: isPositive ? '#065f46' : '#991b1b',
          lineHeight: '1.5'
        }}>
          {anomaly.severity === 'critical' && !isPositive &&
            `Este ano apresentou o maior corte orçamentário da série histórica, com redução de ${Math.abs(anomaly.percentageDeviation).toFixed(1)}% em relação à média. O impacto foi significativo em todas as áreas da educação.`
          }
          {anomaly.severity === 'critical' && isPositive &&
            `Este ano teve o maior aumento orçamentário da série, com expansão de ${anomaly.percentageDeviation.toFixed(1)}% acima da média. Representa um investimento excepcional em educação.`
          }
          {anomaly.severity === 'moderate' && !isPositive &&
            `Redução orçamentária moderada de ${Math.abs(anomaly.percentageDeviation).toFixed(1)}%, possivelmente relacionada a ajustes fiscais ou mudanças de prioridade governamental.`
          }
          {anomaly.severity === 'moderate' && isPositive &&
            `Aumento moderado de ${anomaly.percentageDeviation.toFixed(1)}% no orçamento, indicando expansão controlada do investimento em educação.`
          }
          {anomaly.severity === 'normal' &&
            `Orçamento dentro da normalidade estatística, sem grandes variações em relação à média histórica.`
          }
        </div>
      </div>
    </div>
  );
};

export default AnomalyCard;
