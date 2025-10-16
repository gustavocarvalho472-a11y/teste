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
      background: 'linear-gradient(135deg, #ffffff 0%, #fafafa 100%)',
      borderRadius: '20px',
      overflow: 'hidden',
      boxShadow: '0 0 0 1px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.02)',
      transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      position: 'relative'
    }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 0 0 1px rgba(124, 58, 237, 0.1), 0 12px 24px rgba(124, 58, 237, 0.08)';
        e.currentTarget.style.transform = 'translateY(-4px) scale(1.01)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 0 0 1px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.02)';
        e.currentTarget.style.transform = 'translateY(0) scale(1)';
      }}
    >
      {/* Gradient overlay sutil */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '140px',
        background: 'linear-gradient(180deg, rgba(124, 58, 237, 0.02) 0%, transparent 100%)',
        pointerEvents: 'none'
      }} />

      {/* Header */}
      <div style={{
        padding: '28px',
        position: 'relative'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: '24px'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '8px'
            }}>
              <h3 style={{
                fontSize: '20px',
                fontWeight: '700',
                color: '#0f172a',
                margin: 0,
                letterSpacing: '-0.3px'
              }}>
                {municipality.name}
              </h3>
              {rank && rank <= 3 && (
                <span className="material-icons" style={{
                  fontSize: '20px',
                  color: rank === 1 ? '#FFD700' : rank === 2 ? '#C0C0C0' : '#CD7F32'
                }}>
                  {rank === 1 ? 'workspace_premium' : rank === 2 ? 'military_tech' : 'emoji_events'}
                </span>
              )}
            </div>
            <div style={{
              fontSize: '13px',
              color: '#64748b',
              fontWeight: '500',
              letterSpacing: '0.2px'
            }}>
              {municipality.state} • {municipality.region}
            </div>
          </div>
          {rank && (
            <div style={{
              background: rank <= 3
                ? 'linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%)'
                : '#f1f5f9',
              color: rank <= 3 ? '#ffffff' : '#64748b',
              fontSize: '14px',
              fontWeight: '700',
              padding: '8px 14px',
              borderRadius: '12px',
              boxShadow: rank <= 3 ? '0 4px 12px rgba(124, 58, 237, 0.2)' : 'none'
            }}>
              #{rank}
            </div>
          )}
        </div>

        {/* Orçamento Disponível - Versão Clean */}
        <div style={{
          background: '#fafafa',
          padding: '24px',
          borderRadius: '16px',
          position: 'relative',
          border: '1px solid #f1f5f9'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '12px'
          }}>
            <div style={{
              width: '3px',
              height: '16px',
              borderRadius: '2px',
              backgroundColor: '#10b981'
            }} />
            <div style={{
              fontSize: '11px',
              fontWeight: '600',
              color: '#64748b',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Disponível Agora
            </div>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'baseline',
            gap: '12px',
            marginBottom: '16px'
          }}>
            <div style={{
              fontSize: '40px',
              fontWeight: '800',
              color: '#0f172a',
              letterSpacing: '-1.5px',
              lineHeight: '1'
            }}>
              {formatCurrency(available, true)}
            </div>
            <div style={{
              background: '#f1f5f9',
              color: '#64748b',
              fontSize: '13px',
              fontWeight: '600',
              padding: '4px 10px',
              borderRadius: '6px'
            }}>
              {percentAvailable.toFixed(1)}%
            </div>
          </div>

          {/* Barra de Progresso - Versão Clean */}
          <div style={{
            marginBottom: '14px'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '10px',
              fontSize: '11px',
              fontWeight: '600',
              color: '#64748b'
            }}>
              <span>Progresso de Execução</span>
              <span style={{
                color: '#0f172a',
                fontSize: '13px',
                fontWeight: '700'
              }}>
                {percentExecuted.toFixed(1)}%
              </span>
            </div>

            {/* Barra com posição relativa para os marcos */}
            <div style={{
              position: 'relative',
              height: '8px',
              backgroundColor: '#e2e8f0',
              borderRadius: '100px',
              overflow: 'visible'
            }}>
              {/* Barra de execução atual */}
              <div style={{
                height: '100%',
                width: `${percentExecuted}%`,
                background: '#10b981',
                borderRadius: '100px',
                transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                position: 'relative',
                zIndex: 1
              }} />

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
            gap: '24px',
            marginTop: '16px',
            paddingTop: '16px',
            borderTop: '1px solid #e5e7eb'
          }}>
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: '10px',
                fontWeight: '600',
                color: '#94a3b8',
                marginBottom: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Executado
              </div>
              <div style={{
                color: '#0f172a',
                fontWeight: '700',
                fontSize: '15px',
                letterSpacing: '-0.3px'
              }}>
                {formatCurrency(comparison.executedAmount, true)}
              </div>
            </div>
            <div style={{
              flex: 1,
              textAlign: 'right'
            }}>
              <div style={{
                fontSize: '10px',
                fontWeight: '600',
                color: '#94a3b8',
                marginBottom: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Total
              </div>
              <div style={{
                color: '#0f172a',
                fontWeight: '700',
                fontSize: '15px',
                letterSpacing: '-0.3px'
              }}>
                {formatCurrency(comparison.referenceAmount, true)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Histórico (Dropdown) */}
      <div style={{
        borderTop: '1px solid #f1f5f9'
      }}>
        <button
          onClick={() => setHistoricoOpen(!historicoOpen)}
          style={{
            width: '100%',
            padding: '20px 28px',
            backgroundColor: 'transparent',
            border: 'none',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'pointer',
            transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#fafafa';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
          }}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <span className="material-icons" style={{
                fontSize: '18px',
                color: '#64748b'
              }}>
                history
              </span>
            </div>
            <span style={{
              fontSize: '13px',
              fontWeight: '700',
              color: '#0f172a',
              letterSpacing: '-0.2px'
            }}>
              Histórico Agosto (2020-2024)
            </span>
          </div>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: '8px',
            background: historicoOpen ? '#f1f5f9' : 'transparent',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '12px',
            color: '#64748b',
            transform: historicoOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'all 0.3s ease'
          }}>
            ▼
          </div>
        </button>

        {/* Conteúdo do Dropdown */}
        <div style={{
          maxHeight: historicoOpen ? '500px' : '0',
          transition: 'max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '0 28px 24px',
            background: '#fafafa'
          }}>
            <table style={{
              width: '100%',
              borderCollapse: 'separate',
              borderSpacing: '0 4px'
            }}>
              <thead>
                <tr>
                  <th style={{
                    textAlign: 'left',
                    padding: '12px 14px',
                    fontSize: '10px',
                    fontWeight: '800',
                    color: '#64748b',
                    textTransform: 'uppercase',
                    letterSpacing: '0.8px'
                  }}>
                    ANO
                  </th>
                  <th style={{
                    textAlign: 'center',
                    padding: '12px 14px',
                    fontSize: '10px',
                    fontWeight: '800',
                    color: '#64748b',
                    textTransform: 'uppercase',
                    letterSpacing: '0.8px'
                  }}>
                    MÊS
                  </th>
                  <th style={{
                    textAlign: 'right',
                    padding: '12px 14px',
                    fontSize: '10px',
                    fontWeight: '800',
                    color: '#64748b',
                    textTransform: 'uppercase',
                    letterSpacing: '0.8px'
                  }}>
                    EXECUTADO
                  </th>
                </tr>
              </thead>
              <tbody>
                {municipality.history.map((item: any, idx: number) => (
                  <tr
                    key={item.year}
                    style={{
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'scale(1.01)';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(124, 58, 237, 0.08)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'scale(1)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <td style={{
                      padding: '14px',
                      fontSize: '15px',
                      fontWeight: '700',
                      color: '#0f172a',
                      backgroundColor: '#ffffff',
                      borderTopLeftRadius: '12px',
                      borderBottomLeftRadius: '12px',
                      letterSpacing: '-0.3px'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}>
                        <div style={{
                          width: '4px',
                          height: '20px',
                          borderRadius: '2px',
                          background: idx === 0 ? '#7c3aed' : idx === 1 ? '#a78bfa' : '#d8b4fe'
                        }} />
                        {item.year}
                      </div>
                    </td>
                    <td style={{
                      padding: '14px',
                      fontSize: '13px',
                      fontWeight: '600',
                      color: '#64748b',
                      textAlign: 'center',
                      backgroundColor: '#ffffff'
                    }}>
                      AGO
                    </td>
                    <td style={{
                      padding: '14px',
                      fontSize: '15px',
                      fontWeight: '700',
                      color: '#0f172a',
                      textAlign: 'right',
                      backgroundColor: '#ffffff',
                      borderTopRightRadius: '12px',
                      borderBottomRightRadius: '12px',
                      letterSpacing: '-0.3px'
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
