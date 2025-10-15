import React from 'react';
import { formatCurrency } from '../utils';

interface ExceptionalPeriod {
  id: string;
  name: string;
  icon: string;
  years: number[];
  description: string;
  avgDeviation: number;
  totalImpact: number;
  color: string;
  recovery?: {
    year: number;
    recovered: number;
  };
}

interface ExceptionalPeriodCardProps {
  period: ExceptionalPeriod;
}

const ExceptionalPeriodCard: React.FC<ExceptionalPeriodCardProps> = ({ period }) => {
  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: `2px solid ${period.color}`,
      transition: 'all 0.3s'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
      e.currentTarget.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.12)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
    }}
    >
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '16px',
        paddingBottom: '16px',
        borderBottom: '1px solid #f5edff'
      }}>
        <div style={{
          fontSize: '36px',
          lineHeight: '1'
        }}>
          {period.icon}
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: '700',
            color: '#2e3138',
            margin: 0,
            marginBottom: '4px'
          }}>
            {period.name}
          </h3>
          <div style={{
            fontSize: '13px',
            color: '#6b7280'
          }}>
            {period.years.join(', ')}
          </div>
        </div>
      </div>

      {/* Description */}
      <p style={{
        fontSize: '14px',
        color: '#4b5563',
        lineHeight: '1.6',
        marginBottom: '20px'
      }}>
        {period.description}
      </p>

      {/* Métricas */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        marginBottom: '16px'
      }}>
        <div style={{
          padding: '16px',
          backgroundColor: '#fef3c7',
          borderRadius: '8px',
          border: '1px solid #fbbf24'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#92400e',
            marginBottom: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Desvio Médio
          </div>
          <div style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#b45309'
          }}>
            {period.avgDeviation.toFixed(1)}%
          </div>
        </div>

        <div style={{
          padding: '16px',
          backgroundColor: '#fee2e2',
          borderRadius: '8px',
          border: '1px solid #f87171'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '600',
            color: '#991b1b',
            marginBottom: '6px',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Impacto Total
          </div>
          <div style={{
            fontSize: '24px',
            fontWeight: '700',
            color: '#dc2626'
          }}>
            {formatCurrency(period.totalImpact, true)}
          </div>
        </div>
      </div>

      {/* Recovery (se houver) */}
      {period.recovery && (
        <div style={{
          padding: '16px',
          backgroundColor: '#d1fae5',
          borderRadius: '8px',
          border: '1px solid #86efac'
        }}>
          <div style={{
            fontSize: '12px',
            fontWeight: '600',
            color: '#065f46',
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            📈 Recuperação
          </div>
          <div style={{
            fontSize: '13px',
            color: '#065f46',
            lineHeight: '1.5'
          }}>
            Em {period.recovery.year}, houve recuperação de{' '}
            <strong>{period.recovery.recovered.toFixed(1)}%</strong> em relação ao período de crise.
          </div>
        </div>
      )}
    </div>
  );
};

export default ExceptionalPeriodCard;
