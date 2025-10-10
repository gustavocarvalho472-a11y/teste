import React from 'react';
import { formatCurrency, formatPercent } from '../utils';

interface KPICardProps {
  title: string;
  currentValue: number;
  comparisonValue: number;
  variation: number;
  isCurrentPeriod?: boolean;
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  currentValue,
  comparisonValue,
  variation,
  isCurrentPeriod = false
}) => {
  const isPositive = variation >= 0;

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff',
      transition: 'transform 0.2s, box-shadow 0.2s',
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-2px)';
      e.currentTarget.style.boxShadow = '0 4px 12px rgba(149, 85, 254, 0.15)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
    }}
    >
      {/* Título */}
      <div style={{
        fontSize: '14px',
        fontWeight: '500',
        color: '#5219a1',
        marginBottom: '16px',
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
      }}>
        {title}
      </div>

      {/* Valor principal */}
      <div style={{
        fontSize: '28px',
        fontWeight: '700',
        color: '#2e3138',
        marginBottom: '12px',
        lineHeight: '1.2'
      }}>
        {formatCurrency(isCurrentPeriod ? currentValue : comparisonValue)}
      </div>

      {/* Variação */}
      {!isCurrentPeriod && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{
            fontSize: '16px',
            fontWeight: '600',
            color: isPositive ? '#10b981' : '#ef4444'
          }}>
            {formatPercent(variation)}
          </span>
          <span style={{
            fontSize: '13px',
            color: '#6b7280'
          }}>
            vs comparativo
          </span>
        </div>
      )}

      {/* Valor de comparação (se for período atual) */}
      {isCurrentPeriod && (
        <div style={{
          fontSize: '13px',
          color: '#6b7280'
        }}>
          Período selecionado
        </div>
      )}
    </div>
  );
};

export default KPICard;
