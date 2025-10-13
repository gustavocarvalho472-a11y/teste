import React, { useState } from 'react';
import { YearlyAnomaly } from '../utils/anomalyDetection';
import { getSeverityColor, getSeverityIcon } from '../utils/anomalyDetection';
import { formatCurrency } from '../utils';

interface AnomalyTimelineProps {
  anomalies: YearlyAnomaly[];
}

const AnomalyTimeline: React.FC<AnomalyTimelineProps> = ({ anomalies }) => {
  const [hoveredYear, setHoveredYear] = useState<number | null>(null);

  const sortedAnomalies = [...anomalies].sort((a, b) => a.year - b.year);

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff'
    }}>
      <h3 style={{
        fontSize: '18px',
        fontWeight: '600',
        color: '#2e3138',
        marginBottom: '8px'
      }}>
        Linha do Tempo de Anomalias
      </h3>
      <p style={{
        fontSize: '13px',
        color: '#6b7280',
        marginBottom: '24px'
      }}>
        Análise estatística do orçamento de educação (2015-2024)
      </p>

      {/* Timeline */}
      <div style={{
        position: 'relative',
        padding: '40px 0',
        marginBottom: '16px'
      }}>
        {/* Linha base */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '0',
          right: '0',
          height: '2px',
          backgroundColor: '#e1cdfe',
          transform: 'translateY(-50%)'
        }} />

        {/* Linha de média */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '0',
          right: '0',
          height: '1px',
          backgroundColor: '#9755fe',
          transform: 'translateY(-50%)',
          borderTop: '2px dashed #9755fe'
        }} />

        {/* Pontos de anomalia */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          position: 'relative',
          alignItems: 'center',
          height: '120px'
        }}>
          {sortedAnomalies.map((anomaly, index) => {
            const isHovered = hoveredYear === anomaly.year;
            const size = anomaly.severity === 'critical' ? 24 :
                         anomaly.severity === 'moderate' ? 20 : 16;

            // Posição vertical baseada no z-score
            const verticalOffset = -anomaly.zScore * 15; // pixels

            return (
              <div
                key={anomaly.year}
                style={{
                  position: 'relative',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  flex: 1
                }}
                onMouseEnter={() => setHoveredYear(anomaly.year)}
                onMouseLeave={() => setHoveredYear(null)}
              >
                {/* Bolha */}
                <div style={{
                  width: `${size}px`,
                  height: `${size}px`,
                  borderRadius: '50%',
                  backgroundColor: getSeverityColor(anomaly.severity),
                  border: '3px solid #ffffff',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  transform: `translateY(${verticalOffset}px) ${isHovered ? 'scale(1.3)' : 'scale(1)'}`,
                  boxShadow: isHovered
                    ? '0 4px 12px rgba(0, 0, 0, 0.2)'
                    : '0 2px 4px rgba(0, 0, 0, 0.1)',
                  zIndex: isHovered ? 10 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: `${size * 0.5}px`
                }}>
                  {anomaly.severity !== 'normal' && getSeverityIcon(anomaly.severity)}
                </div>

                {/* Ano */}
                <div style={{
                  marginTop: '60px',
                  fontSize: '11px',
                  fontWeight: isHovered ? '700' : '500',
                  color: isHovered ? '#3f127d' : '#6b7280',
                  transition: 'all 0.2s'
                }}>
                  {anomaly.year}
                </div>

                {/* Ícones de evento */}
                {anomaly.events.length > 0 && (
                  <div style={{
                    marginTop: '-52px',
                    fontSize: '14px',
                    display: 'flex',
                    gap: '2px'
                  }}>
                    {anomaly.events.map((event, i) => (
                      <span key={i} title={event}>
                        {event.split(' ')[0]}
                      </span>
                    ))}
                  </div>
                )}

                {/* Tooltip */}
                {isHovered && (
                  <div style={{
                    position: 'absolute',
                    top: verticalOffset < 0 ? 'auto' : '-180px',
                    bottom: verticalOffset < 0 ? '-180px' : 'auto',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    backgroundColor: '#2e3138',
                    color: '#ffffff',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
                    minWidth: '250px',
                    zIndex: 100,
                    fontSize: '12px',
                    lineHeight: '1.6',
                    pointerEvents: 'none'
                  }}>
                    <div style={{ fontWeight: '700', fontSize: '14px', marginBottom: '8px' }}>
                      {anomaly.year} - {anomaly.governmentContext}
                    </div>
                    <div style={{ marginBottom: '4px' }}>
                      <strong>Valor:</strong> {formatCurrency(anomaly.value, true)}
                    </div>
                    <div style={{ marginBottom: '4px' }}>
                      <strong>Desvio:</strong> {anomaly.percentageDeviation >= 0 ? '+' : ''}{anomaly.percentageDeviation.toFixed(1)}%
                    </div>
                    <div style={{ marginBottom: '4px' }}>
                      <strong>Z-score:</strong> {anomaly.zScore.toFixed(2)}σ
                    </div>
                    {anomaly.events.length > 0 && (
                      <div style={{
                        marginTop: '8px',
                        paddingTop: '8px',
                        borderTop: '1px solid #4b5563'
                      }}>
                        {anomaly.events.map((event, i) => (
                          <div key={i} style={{ fontSize: '11px', marginTop: '2px' }}>
                            {event}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legenda */}
      <div style={{
        display: 'flex',
        gap: '24px',
        justifyContent: 'center',
        paddingTop: '16px',
        borderTop: '1px solid #f5edff',
        fontSize: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: '#ef4444'
          }} />
          <span style={{ color: '#6b7280' }}>Crítico (&gt;3σ)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: '#f59e0b'
          }} />
          <span style={{ color: '#6b7280' }}>Moderado (&gt;2σ)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: '#10b981'
          }} />
          <span style={{ color: '#6b7280' }}>Normal (&lt;2σ)</span>
        </div>
      </div>
    </div>
  );
};

export default AnomalyTimeline;
