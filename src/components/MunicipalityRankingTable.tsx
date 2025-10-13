import React, { useState } from 'react';
import { MunicipalityBudget, ComparisonMode } from '../types/municipality';
import { formatCurrency } from '../utils';

interface MunicipalityRankingTableProps {
  municipalities: MunicipalityBudget[];
  comparisonMode: ComparisonMode;
}

const MunicipalityRankingTable: React.FC<MunicipalityRankingTableProps> = ({
  municipalities,
  comparisonMode
}) => {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const getComparison = (mun: MunicipalityBudget) => {
    switch (comparisonMode) {
      case 'avg-electoral': return mun.comparison.avgElectoral;
      case 'last-electoral': return mun.comparison.lastElectoral;
      case 'avg-all': return mun.comparison.avgAll;
      case 'previous-year': return mun.comparison.previousYear;
    }
  };

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '12px',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      border: '1px solid #f5edff',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '20px 24px',
        borderBottom: '2px solid #f5edff',
        backgroundColor: '#f9f4ff'
      }}>
        <h3 style={{
          fontSize: '18px',
          fontWeight: '600',
          color: '#2e3138',
          margin: 0
        }}>
          📋 Ranking Completo de Subexecução
        </h3>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse'
        }}>
          <thead>
            <tr style={{
              backgroundColor: '#f9f4ff',
              borderBottom: '2px solid #e1cdfe'
            }}>
              <th style={{
                padding: '16px 20px',
                textAlign: 'left',
                fontSize: '12px',
                fontWeight: '700',
                color: '#5219a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                #
              </th>
              <th style={{
                padding: '16px 20px',
                textAlign: 'left',
                fontSize: '12px',
                fontWeight: '700',
                color: '#5219a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Município
              </th>
              <th style={{
                padding: '16px 20px',
                textAlign: 'right',
                fontSize: '12px',
                fontWeight: '700',
                color: '#5219a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Sobrando Extra
              </th>
              <th style={{
                padding: '16px 20px',
                textAlign: 'right',
                fontSize: '12px',
                fontWeight: '700',
                color: '#5219a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                % Executado
              </th>
              <th style={{
                padding: '16px 20px',
                textAlign: 'right',
                fontSize: '12px',
                fontWeight: '700',
                color: '#5219a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Variação
              </th>
              <th style={{
                padding: '16px 20px',
                textAlign: 'center',
                fontSize: '12px',
                fontWeight: '700',
                color: '#5219a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Status
              </th>
              <th style={{
                padding: '16px 20px',
                textAlign: 'center',
                fontSize: '12px',
                fontWeight: '700',
                color: '#5219a1',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Ação
              </th>
            </tr>
          </thead>
          <tbody>
            {municipalities.map((mun, index) => {
              const comparison = getComparison(mun);
              const isExpanded = expandedRow === mun.id;
              const severityColor = comparison.severity === 'critical' ? '#ef4444' :
                                   comparison.severity === 'moderate' ? '#f59e0b' : '#10b981';

              return (
                <React.Fragment key={mun.id}>
                  <tr style={{
                    borderBottom: '1px solid #f5edff',
                    transition: 'background-color 0.2s',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f9f4ff';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                  onClick={() => setExpandedRow(isExpanded ? null : mun.id)}
                  >
                    <td style={{
                      padding: '16px 20px',
                      fontSize: '14px',
                      fontWeight: '700',
                      color: '#3f127d'
                    }}>
                      {index + 1}
                    </td>
                    <td style={{ padding: '16px 20px' }}>
                      <div style={{
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#2e3138',
                        marginBottom: '4px'
                      }}>
                        {mun.name}
                      </div>
                      <div style={{
                        fontSize: '12px',
                        color: '#6b7280'
                      }}>
                        {mun.state} · {mun.region}
                      </div>
                    </td>
                    <td style={{
                      padding: '16px 20px',
                      textAlign: 'right',
                      fontSize: '14px',
                      fontWeight: '700',
                      color: '#ef4444'
                    }}>
                      {formatCurrency(comparison.extraAvailable, true)}
                    </td>
                    <td style={{
                      padding: '16px 20px',
                      textAlign: 'right',
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#2e3138'
                    }}>
                      {mun.executionRate.toFixed(1)}%
                    </td>
                    <td style={{
                      padding: '16px 20px',
                      textAlign: 'right',
                      fontSize: '14px',
                      fontWeight: '700',
                      color: comparison.difference < 0 ? '#ef4444' : '#10b981'
                    }}>
                      {comparison.percentageDiff.toFixed(1)}%
                    </td>
                    <td style={{
                      padding: '16px 20px',
                      textAlign: 'center'
                    }}>
                      <span style={{
                        padding: '4px 10px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: '700',
                        color: severityColor,
                        backgroundColor: comparison.severity === 'critical' ? '#fee2e2' :
                                       comparison.severity === 'moderate' ? '#fef3c7' : '#d1fae5',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px'
                      }}>
                        {comparison.severity === 'critical' ? '🔴' :
                         comparison.severity === 'moderate' ? '🟡' : '🟢'}
                      </span>
                    </td>
                    <td style={{
                      padding: '16px 20px',
                      textAlign: 'center'
                    }}>
                      <button style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        border: '1px solid #d1b3ff',
                        backgroundColor: '#ffffff',
                        color: '#5219a1',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#f5edff';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = '#ffffff';
                      }}
                      >
                        {isExpanded ? '▲ Fechar' : '▼ Ver'}
                      </button>
                    </td>
                  </tr>

                  {/* Linha Expandida */}
                  {isExpanded && (
                    <tr>
                      <td colSpan={7} style={{
                        padding: '24px',
                        backgroundColor: '#f9f4ff',
                        borderBottom: '2px solid #e1cdfe'
                      }}>
                        <div style={{
                          display: 'grid',
                          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                          gap: '16px'
                        }}>
                          {/* Orçamento Total */}
                          <div>
                            <div style={{
                              fontSize: '11px',
                              fontWeight: '600',
                              color: '#5219a1',
                              marginBottom: '6px'
                            }}>
                              Orçamento Total 2024
                            </div>
                            <div style={{
                              fontSize: '18px',
                              fontWeight: '700',
                              color: '#2e3138'
                            }}>
                              {formatCurrency(mun.totalBudget, true)}
                            </div>
                          </div>

                          {/* Executado */}
                          <div>
                            <div style={{
                              fontSize: '11px',
                              fontWeight: '600',
                              color: '#5219a1',
                              marginBottom: '6px'
                            }}>
                              Executado
                            </div>
                            <div style={{
                              fontSize: '18px',
                              fontWeight: '700',
                              color: '#2e3138'
                            }}>
                              {formatCurrency(mun.executed, true)}
                            </div>
                          </div>

                          {/* Disponível */}
                          <div>
                            <div style={{
                              fontSize: '11px',
                              fontWeight: '600',
                              color: '#5219a1',
                              marginBottom: '6px'
                            }}>
                              Disponível
                            </div>
                            <div style={{
                              fontSize: '18px',
                              fontWeight: '700',
                              color: '#ef4444'
                            }}>
                              {formatCurrency(mun.available, true)}
                            </div>
                          </div>

                          {/* Referência */}
                          <div>
                            <div style={{
                              fontSize: '11px',
                              fontWeight: '600',
                              color: '#5219a1',
                              marginBottom: '6px'
                            }}>
                              Referência ({comparison.referencePeriod})
                            </div>
                            <div style={{
                              fontSize: '18px',
                              fontWeight: '700',
                              color: '#2e3138'
                            }}>
                              {formatCurrency(comparison.referenceValue, true)}
                            </div>
                          </div>
                        </div>

                        {/* Eventos */}
                        {mun.events.length > 0 && (
                          <div style={{
                            marginTop: '16px',
                            display: 'flex',
                            gap: '8px',
                            flexWrap: 'wrap'
                          }}>
                            {mun.events.map((event, i) => (
                              <span
                                key={i}
                                style={{
                                  fontSize: '11px',
                                  padding: '4px 10px',
                                  backgroundColor: '#e1cdfe',
                                  borderRadius: '4px',
                                  color: '#5219a1',
                                  fontWeight: '600'
                                }}
                              >
                                {event}
                              </span>
                            ))}
                          </div>
                        )}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MunicipalityRankingTable;
