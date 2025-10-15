// Componente de Card para Municípios Prioritários
// Design baseado no sketch: compacto, foco no orçamento disponível

import React, { useState } from 'react';
import { formatCurrency } from '../utils';

interface MunicipalityData {
  id: string;
  name: string;
  state: string;
  budget: {
    total: number;
    executed: number;
    available: number;
    percentExecuted: number;
  };
  history: Array<{
    year: number;
    month: number;
    available: number;
  }>;
  rank?: number;
}

interface PriorityMunicipalityCardProps {
  municipality: any; // Tipo do municipalityBudgetData
  comparisonMode: 'avg-electoral' | 'last-electoral' | 'avg-all' | 'previous-year';
  rank?: number;
}

const COLORS = {
  purple600: '#6941C6',
  purple100: '#E9D7FE',
  purple50: '#F4EBFF',
  textPrimary: '#1A1A1A',
  textSecondary: '#525252',
  textTertiary: '#A3A3A3',
  borderLight: '#F0F0F0',
  bgPrimary: '#FFFFFF',
  green: '#10b981',
  greenLight: '#d1fae5',
};

const PriorityMunicipalityCard: React.FC<PriorityMunicipalityCardProps> = ({
  municipality,
  comparisonMode,
  rank
}) => {
  const [historicoOpen, setHistoricoOpen] = useState(false);
  const [hoveredYear, setHoveredYear] = useState<number | null>(null);

  // Pegar dados da comparação
  const getComparison = () => {
    switch (comparisonMode) {
      case 'avg-electoral': return municipality.comparison.avgElectoral;
      case 'last-electoral': return municipality.comparison.lastElectoral;
      case 'avg-all': return municipality.comparison.avgAll;
      case 'previous-year': return municipality.comparison.previousYear;
    }
  };

  const comparison = getComparison();
  const available = comparison.referenceAmount - comparison.executedAmount;
  const percentExecuted = (comparison.executedAmount / comparison.referenceAmount) * 100;
  const percentAvailable = 100 - percentExecuted;

  // Calcular quais marcadores estão próximos (dentro de 5%)
  const historicalData = municipality.history.slice(0, 3).map((item: any, index: number) => ({
    year: item.year,
    executed: item.executed,
    totalBudget: item.totalBudget,
    percent: (item.executed / item.totalBudget) * 100, // Usa o orçamento do próprio ano
    color: index === 0 ? '#6941C6' : index === 1 ? '#9E77ED' : '#D6BBFB'
  }));

  const getCloseMarkers = (targetPercent: number) => {
    return historicalData.filter(data => Math.abs(data.percent - targetPercent) < 5);
  };

  return (
    <div style={{
      backgroundColor: COLORS.bgPrimary,
      borderRadius: '12px',
      border: `2px solid ${COLORS.borderLight}`,
      overflow: 'hidden',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      transition: 'all 0.2s'
    }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 16px rgba(105, 65, 198, 0.15)';
        e.currentTarget.style.borderColor = COLORS.purple600;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
        e.currentTarget.style.borderColor = COLORS.borderLight;
      }}
    >
      {/* Header */}
      <div style={{
        padding: '20px',
        borderBottom: `1px solid ${COLORS.borderLight}`
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '12px'
        }}>
          <div>
            <h3 style={{
              fontSize: '20px',
              fontWeight: '700',
              color: COLORS.textPrimary,
              margin: 0,
              marginBottom: '4px'
            }}>
              {municipality.name}
            </h3>
            <div style={{
              fontSize: '13px',
              color: COLORS.textSecondary,
              fontWeight: '600'
            }}>
              {municipality.state} · {municipality.region}
            </div>
          </div>
          {rank && (
            <div style={{
              backgroundColor: COLORS.purple50,
              color: COLORS.purple600,
              fontSize: '14px',
              fontWeight: '700',
              padding: '6px 12px',
              borderRadius: '8px'
            }}>
              #{rank}
            </div>
          )}
        </div>

        {/* Orçamento Disponível */}
        <div style={{
          backgroundColor: COLORS.greenLight,
          padding: '16px',
          borderRadius: '8px',
          border: `2px solid ${COLORS.green}`
        }}>
          <div style={{
            fontSize: '11px',
            fontWeight: '700',
            color: '#065f46',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '8px'
          }}>
            ORÇAMENTO DISPONÍVEL (AGO/2025)
          </div>
          <div style={{
            fontSize: '28px',
            fontWeight: '700',
            color: COLORS.green,
            lineHeight: '1',
            marginBottom: '12px'
          }}>
            {formatCurrency(available, true)}
          </div>

          {/* Barra de Progresso com Marcos Históricos */}
          <div style={{
            marginBottom: '8px'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '6px',
              fontSize: '11px',
              fontWeight: '600'
            }}>
              <span style={{ color: '#065f46' }}>Executado em Agosto/2025</span>
              <span style={{ color: '#065f46' }}>{percentExecuted.toFixed(1)}%</span>
            </div>

            {/* Barra com posição relativa para os marcos */}
            <div style={{
              position: 'relative',
              height: '24px',
              backgroundColor: '#E5E7EB',
              borderRadius: '4px',
              overflow: 'visible'
            }}>
              {/* Barra de execução atual */}
              <div style={{
                height: '100%',
                width: `${percentExecuted}%`,
                backgroundColor: COLORS.green,
                borderRadius: '4px',
                transition: 'width 0.5s ease',
                position: 'relative',
                zIndex: 1
              }}></div>

              {/* Marcos dos anos anteriores */}
              {historicalData.map((data, index) => {
                const isHovered = hoveredYear === data.year;
                const closeMarkers = getCloseMarkers(data.percent);
                const isMultiple = closeMarkers.length > 1;

                return (
                  <React.Fragment key={data.year}>
                    {/* Área de hover expandida (hitbox invisível) */}
                    <div
                      style={{
                        position: 'absolute',
                        left: `${Math.min(data.percent, 100)}%`,
                        top: '-4px',
                        height: 'calc(100% + 8px)',
                        width: '16px',
                        transform: 'translateX(-50%)',
                        cursor: 'pointer',
                        zIndex: 3
                      }}
                      onMouseEnter={() => setHoveredYear(data.year)}
                      onMouseLeave={() => setHoveredYear(null)}
                    />

                    {/* Marcador visual */}
                    <div
                      style={{
                        position: 'absolute',
                        left: `${Math.min(data.percent, 100)}%`,
                        top: '0',
                        height: '100%',
                        width: isHovered ? '5px' : '3px',
                        backgroundColor: data.color,
                        zIndex: 2,
                        transform: 'translateX(-50%)',
                        transition: 'width 0.2s ease',
                        pointerEvents: 'none'
                      }}
                    />

                    {/* Tooltip - mostra múltiplos anos se próximos */}
                    {isHovered && (
                      <div style={{
                        position: 'absolute',
                        bottom: '100%',
                        left: `${Math.min(data.percent, 100)}%`,
                        transform: 'translateX(-50%)',
                        marginBottom: '8px',
                        backgroundColor: '#1A1A1A',
                        color: '#FFFFFF',
                        padding: '8px 12px',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: '600',
                        whiteSpace: 'nowrap',
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
                        zIndex: 100,
                        pointerEvents: 'none'
                      }}>
                        {isMultiple ? (
                          // Tooltip consolidado para marcadores próximos
                          <>
                            <div style={{
                              fontSize: '10px',
                              color: '#A3A3A3',
                              marginBottom: '6px',
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              AGOSTO {closeMarkers.map(m => m.year).join('-')}
                            </div>
                            {closeMarkers.map((marker, idx) => (
                              <div key={marker.year} style={{
                                marginBottom: idx < closeMarkers.length - 1 ? '6px' : '0',
                                paddingBottom: idx < closeMarkers.length - 1 ? '6px' : '0',
                                borderBottom: idx < closeMarkers.length - 1 ? '1px solid #333' : 'none'
                              }}>
                                <div style={{
                                  fontSize: '12px',
                                  fontWeight: '700',
                                  marginBottom: '2px',
                                  color: marker.color
                                }}>
                                  {marker.year}: {marker.percent.toFixed(1)}% executado
                                </div>
                                <div style={{
                                  fontSize: '11px',
                                  color: '#10b981'
                                }}>
                                  {formatCurrency(marker.totalBudget - marker.executed, true)} disponível
                                </div>
                              </div>
                            ))}
                          </>
                        ) : (
                          // Tooltip individual
                          <>
                            <div style={{
                              fontSize: '10px',
                              color: '#A3A3A3',
                              marginBottom: '4px',
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}>
                              AGOSTO {data.year}
                            </div>
                            <div style={{
                              fontSize: '13px',
                              fontWeight: '700',
                              marginBottom: '2px'
                            }}>
                              {data.percent.toFixed(1)}% executado
                            </div>
                            <div style={{
                              fontSize: '11px',
                              color: '#10b981'
                            }}>
                              {formatCurrency(data.totalBudget - data.executed, true)} disponível
                            </div>
                          </>
                        )}

                        {/* Arrow */}
                        <div style={{
                          position: 'absolute',
                          top: '100%',
                          left: '50%',
                          transform: 'translateX(-50%)',
                          width: 0,
                          height: 0,
                          borderLeft: '6px solid transparent',
                          borderRight: '6px solid transparent',
                          borderTop: '6px solid #1A1A1A'
                        }}></div>
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>

            {/* Legenda dos marcos */}
            <div style={{
              display: 'flex',
              gap: '12px',
              marginTop: '12px',
              fontSize: '10px',
              fontWeight: '600',
              color: COLORS.textTertiary
            }}>
              {historicalData.map((data) => (
                <div key={data.year} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: data.color,
                    borderRadius: '2px'
                  }}></div>
                  <span>{data.year}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '12px',
            color: '#065f46'
          }}>
            <span>Executado: {formatCurrency(comparison.executedAmount, true)}</span>
            <span>Total: {formatCurrency(comparison.referenceAmount, true)}</span>
          </div>
        </div>
      </div>

      {/* Histórico (Dropdown) */}
      <div>
        <button
          onClick={() => setHistoricoOpen(!historicoOpen)}
          style={{
            width: '100%',
            padding: '16px 20px',
            backgroundColor: 'transparent',
            border: 'none',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#F9FAFB';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ fontSize: '16px' }}>📊</span>
            <span style={{
              fontSize: '13px',
              fontWeight: '700',
              color: COLORS.textPrimary,
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              HISTÓRICO (Agosto - 2020 a 2024)
            </span>
          </div>
          <div style={{
            fontSize: '16px',
            color: COLORS.textSecondary,
            transform: historicoOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s ease'
          }}>
            ▼
          </div>
        </button>

        {/* Conteúdo do Dropdown */}
        <div style={{
          maxHeight: historicoOpen ? '400px' : '0',
          transition: 'max-height 0.4s ease-in-out',
          overflow: 'hidden'
        }}>
          <div style={{ padding: '0 20px 20px' }}>
            <table style={{
              width: '100%',
              borderCollapse: 'collapse'
            }}>
              <thead>
                <tr style={{
                  borderBottom: '2px solid #D1D5DB'
                }}>
                  <th style={{
                    textAlign: 'left',
                    padding: '12px 8px',
                    fontSize: '11px',
                    fontWeight: '700',
                    color: COLORS.textSecondary,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    ANO
                  </th>
                  <th style={{
                    textAlign: 'center',
                    padding: '12px 8px',
                    fontSize: '11px',
                    fontWeight: '700',
                    color: COLORS.textSecondary,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    MÊS
                  </th>
                  <th style={{
                    textAlign: 'right',
                    padding: '12px 8px',
                    fontSize: '11px',
                    fontWeight: '700',
                    color: COLORS.textSecondary,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px'
                  }}>
                    DISPONÍVEL
                  </th>
                </tr>
              </thead>
              <tbody>
                {municipality.history.map((item: any) => (
                  <tr
                    key={item.year}
                    style={{
                      borderBottom: '1px solid #E5E7EB',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#F9FAFB';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <td style={{
                      padding: '12px 8px',
                      fontSize: '14px',
                      fontWeight: '700',
                      color: COLORS.textPrimary
                    }}>
                      {item.year}
                    </td>
                    <td style={{
                      padding: '12px 8px',
                      fontSize: '14px',
                      fontWeight: '600',
                      color: COLORS.textSecondary,
                      textAlign: 'center'
                    }}>
                      08
                    </td>
                    <td style={{
                      padding: '12px 8px',
                      fontSize: '14px',
                      fontWeight: '600',
                      color: COLORS.textPrimary,
                      textAlign: 'right'
                    }}>
                      {formatCurrency(item.executed, true)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PriorityMunicipalityCard;
