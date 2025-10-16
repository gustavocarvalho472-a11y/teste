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

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
      border: '1px solid #f3f4f6',
      position: 'relative',
      transition: 'all 0.2s',
      overflow: 'hidden'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-4px)';
      e.currentTarget.style.boxShadow = '0 8px 24px rgba(124, 58, 237, 0.12)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
    }}
    >
      {/* Barra superior colorida sutil */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        background: 'linear-gradient(90deg, #7C3AED 0%, #A78BFA 100%)'
      }} />

      {/* Badge de Ranking */}
      {rank && (
        <div style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          backgroundColor: '#F9FAFB',
          color: '#6B7280',
          padding: '4px 12px',
          borderRadius: '12px',
          fontSize: '12px',
          fontWeight: '700',
          border: '1px solid #E5E7EB'
        }}>
          #{rank}
        </div>
      )}

      {/* Header */}
      <div style={{
        marginBottom: '20px',
        paddingTop: '4px'
      }}>
        <h3 style={{
          fontSize: '20px',
          fontWeight: '700',
          color: '#111827',
          margin: '0 0 6px 0',
          letterSpacing: '-0.01em'
        }}>
          {municipality.name}
        </h3>
        <div style={{
          fontSize: '13px',
          color: '#9CA3AF',
          fontWeight: '500',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <span>{municipality.state}</span>
          <span style={{ color: '#D1D5DB' }}>•</span>
          <span>{municipality.region}</span>
        </div>
      </div>

      {/* Métricas Principais */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '12px',
        marginBottom: '18px'
      }}>
        <div style={{
          padding: '18px',
          background: 'linear-gradient(135deg, #FAFBFC 0%, #F9FAFB 100%)',
          borderRadius: '12px',
          border: '1px solid #F3F4F6'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '700',
            color: '#9CA3AF',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.8px'
          }}>
            Disponível
          </div>
          <div style={{
            fontSize: '22px',
            fontWeight: '800',
            color: '#7C3AED',
            marginBottom: '4px',
            letterSpacing: '-0.02em'
          }}>
            {formatCurrency(extraAvailable, true)}
          </div>
          <div style={{
            fontSize: '11px',
            color: '#9CA3AF',
            fontWeight: '500'
          }}>
            vs Referência
          </div>
        </div>

        <div style={{
          padding: '18px',
          background: 'linear-gradient(135deg, #FAFBFC 0%, #F9FAFB 100%)',
          borderRadius: '12px',
          border: '1px solid #F3F4F6'
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '700',
            color: '#9CA3AF',
            marginBottom: '8px',
            textTransform: 'uppercase',
            letterSpacing: '0.8px'
          }}>
            Executado
          </div>
          <div style={{
            fontSize: '22px',
            fontWeight: '800',
            color: '#111827',
            marginBottom: '4px',
            letterSpacing: '-0.02em'
          }}>
            {municipality.executionRate.toFixed(1)}%
          </div>
          <div style={{
            fontSize: '11px',
            color: '#9CA3AF',
            fontWeight: '500'
          }}>
            de R$ {(municipality.totalBudget / 1000000000).toFixed(1)}bi
          </div>
        </div>
      </div>

      {/* Desvio destacado */}
      <div style={{
        padding: '16px',
        background: percentageDiff < -10
          ? 'linear-gradient(135deg, #FEF3F2 0%, #FEE2E2 100%)'
          : 'linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%)',
        borderRadius: '12px',
        marginBottom: '16px',
        border: `1px solid ${percentageDiff < -10 ? '#FEE2E2' : '#E5E7EB'}`
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: '#9CA3AF',
              marginBottom: '4px',
              textTransform: 'uppercase',
              letterSpacing: '0.8px'
            }}>
              Desvio do Padrão
            </div>
            <div style={{
              fontSize: '28px',
              fontWeight: '800',
              color: percentageDiff < -10 ? '#DC2626' : '#374151',
              letterSpacing: '-0.02em'
            }}>
              {percentageDiff.toFixed(1)}%
            </div>
          </div>
          <div style={{
            textAlign: 'right'
          }}>
            <div style={{
              fontSize: '10px',
              color: '#9CA3AF',
              marginBottom: '2px',
              fontWeight: '600'
            }}>
              Referência
            </div>
            <div style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#6B7280',
              marginBottom: '6px'
            }}>
              {formatCurrency(comparison.referenceAmount, true)}
            </div>
            <div style={{
              fontSize: '10px',
              color: '#9CA3AF',
              marginBottom: '2px',
              fontWeight: '600'
            }}>
              Executado
            </div>
            <div style={{
              fontSize: '13px',
              fontWeight: '600',
              color: '#6B7280'
            }}>
              {formatCurrency(comparison.executedAmount, true)}
            </div>
          </div>
        </div>
      </div>

      {/* Contexto */}
      {municipality.events.length > 0 && (
        <div style={{
          display: 'flex',
          gap: '6px',
          flexWrap: 'wrap'
        }}>
          {municipality.events.map((event, i) => (
            <span
              key={i}
              style={{
                fontSize: '10px',
                padding: '5px 10px',
                backgroundColor: '#F9FAFB',
                borderRadius: '6px',
                color: '#6B7280',
                fontWeight: '600',
                border: '1px solid #F3F4F6',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}
            >
              {event}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default MunicipalityCard;
