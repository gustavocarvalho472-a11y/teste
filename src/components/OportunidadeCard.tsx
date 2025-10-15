// P1 - Componente OportunidadeCard (Com Dropdown Histórico)

import React, { useState } from 'react';
import { OportunidadeData, OPPORTUNITY_COLORS } from '../types/oportunidade';
import { formatters } from '../utils/oportunidadeCalculator';

interface OportunidadeCardProps {
  data: OportunidadeData;
}

const OportunidadeCard: React.FC<OportunidadeCardProps> = ({ data }) => {
  const colors = OPPORTUNITY_COLORS[data.nivel];
  const [historicoOpen, setHistoricoOpen] = useState(false);

  return (
    <div style={{
      backgroundColor: '#FFFFFF',
      borderRadius: '16px',
      overflow: 'hidden',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      transition: 'all 0.3s ease',
    }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.15)';
        e.currentTarget.style.transform = 'translateY(-4px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      {/* Header Colorido */}
      <div style={{
        background: colors.gradient,
        padding: '24px 32px',
        color: '#FFFFFF'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h3 style={{
              fontSize: '28px',
              fontWeight: '700',
              marginBottom: '4px',
              lineHeight: '1.2'
            }}>
              {data.municipio}
            </h3>
            <p style={{
              fontSize: '14px',
              opacity: 0.9,
              margin: 0
            }}>
              {data.estado} · {data.categoria}
            </p>
          </div>
          <div style={{
            padding: '8px 16px',
            borderRadius: '20px',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)',
            border: '2px solid rgba(255, 255, 255, 0.3)',
            fontSize: '12px',
            fontWeight: '700',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            💎 {data.nivel === 'PREMIUM' ? 'Premium' : data.nivel === 'FORTE' ? 'Forte' : 'Boa'}
          </div>
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: '32px' }}>
        {/* Métrica Principal */}
        <div style={{
          background: `linear-gradient(135deg, ${colors.light} 0%, ${colors.light}ee 100%)`,
          borderRadius: '16px',
          padding: '24px',
          marginBottom: '24px',
          border: `2px solid ${colors.border}`,
          display: 'flex',
          alignItems: 'center',
          gap: '20px'
        }}>
          <div style={{ fontSize: '48px' }}>💰</div>
          <div style={{ flex: 1 }}>
            <div style={{
              fontSize: '11px',
              fontWeight: '700',
              color: colors.text,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '8px'
            }}>
              Orçamento Disponível
            </div>
            <div style={{
              fontSize: '40px',
              fontWeight: '700',
              color: '#1A1A1A',
              lineHeight: '1',
              marginBottom: '8px'
            }}>
              {formatters.currency(data.orcamento.disponivel)}
            </div>
            <div style={{
              fontSize: '14px',
              fontWeight: '600',
              color: colors.text
            }}>
              {data.orcamento.percentualDisponivel.toFixed(1)}% do orçamento total
            </div>
          </div>
        </div>

        {/* Grid 3 Métricas */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '12px',
          marginBottom: '24px'
        }}>
          <MetricBox
            label="Orçamento Anual"
            value={formatters.currency(data.orcamento.total)}
            subtitle="Média 2020-24"
          />
          <MetricBox
            label="Executado"
            value={formatters.currency(data.orcamento.executado)}
            subtitle="Jan-Mai 2025"
          />
          <MetricBox
            label="Contratos"
            value={formatters.number(data.contratos.fechados)}
            subtitle="Fechados"
          />
        </div>

        {/* Barra de Execução */}
        <div style={{
          backgroundColor: '#F7F7F7',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '24px'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginBottom: '12px'
          }}>
            <span style={{
              fontSize: '14px',
              fontWeight: '700',
              color: '#4B5563'
            }}>
              Execução Orçamentária 2025
            </span>
            <span style={{
              fontSize: '14px',
              fontWeight: '700',
              color: colors.primary
            }}>
              {data.orcamento.percentualExecutado.toFixed(1)}% executado
            </span>
          </div>

          <div style={{
            height: '24px',
            backgroundColor: '#E5E7EB',
            borderRadius: '12px',
            overflow: 'hidden',
            position: 'relative'
          }}>
            <div style={{
              height: '100%',
              width: `${data.orcamento.percentualExecutado}%`,
              background: colors.gradient,
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              paddingRight: '12px',
              transition: 'width 0.7s ease'
            }}>
              <span style={{
                fontSize: '12px',
                fontWeight: '700',
                color: '#FFFFFF'
              }}>
                {data.orcamento.percentualExecutado.toFixed(1)}%
              </span>
            </div>
          </div>

          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: '8px',
            fontSize: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: colors.primary
              }}></div>
              <span style={{ color: '#6B7280' }}>
                Executado: {formatters.currency(data.orcamento.executado)}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: '#D1D5DB'
              }}></div>
              <span style={{ color: '#6B7280' }}>
                Disponível: {formatters.currency(data.orcamento.disponivel)}
              </span>
            </div>
          </div>
        </div>

        {/* Grid 2x2 Oportunidades */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '12px',
          marginBottom: '24px'
        }}>
          <OppBox
            label="Editais Ativos"
            value={formatters.number(data.oportunidades.editaisAtivos)}
            subtitle={`${formatters.currency(data.oportunidades.valorEditais)} em licitação`}
          />
          <OppBox
            label="Gap vs Média"
            value={formatters.percent(data.contratos.gapPercentual)}
            subtitle={`${Math.abs(data.contratos.gap)} contratos abaixo`}
          />
          <OppBox
            label="Orçamento Livre"
            value={formatters.currency(data.oportunidades.orcamentoLivre)}
            subtitle="Sem edital ainda"
          />
          <OppBox
            label="Projeção Ano"
            value={formatters.number(data.contratos.projecaoAno)}
            subtitle={`contratos (vs ${formatters.number(data.contratos.mediaAnual)} média)`}
          />
        </div>

        {/* Comparação Compacta */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '12px',
          marginBottom: '24px'
        }}>
          <CompBox
            label="Esperado até Maio"
            value={`${formatters.number(data.comparacao.esperadoContratos)} contratos`}
            diff={`Real: ${formatters.number(data.comparacao.realContratos)} (${formatters.percent(data.contratos.gapPercentual)})`}
          />
          <CompBox
            label="Esperado até Maio"
            value={formatters.currency(data.comparacao.esperadoValor)}
            diff={`Real: ${formatters.currency(data.comparacao.realValor)} (${formatters.percent(data.oportunidades.diferencaFinanceiraPercent)})`}
          />
        </div>

        {/* Dropdown Histórico */}
        <div style={{
          backgroundColor: '#F7F7F7',
          borderRadius: '12px',
          border: '2px solid #E5E7EB',
          marginBottom: '24px',
          overflow: 'hidden'
        }}>
          {/* Header do Dropdown */}
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
              e.currentTarget.style.backgroundColor = '#E5E7EB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}>
              <span style={{ fontSize: '20px' }}>📊</span>
              <span style={{
                fontSize: '14px',
                fontWeight: '700',
                color: '#1A1A1A'
              }}>
                Histórico 2020-2024
              </span>
              <span style={{
                fontSize: '12px',
                fontWeight: '600',
                color: '#6B7280',
                backgroundColor: '#E5E7EB',
                padding: '4px 12px',
                borderRadius: '12px'
              }}>
                {data.historico.length} anos
              </span>
            </div>
            <div style={{
              fontSize: '20px',
              color: '#6B7280',
              transform: historicoOpen ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.3s ease'
            }}>
              ▼
            </div>
          </button>

          {/* Conteúdo do Dropdown */}
          <div style={{
            maxHeight: historicoOpen ? '500px' : '0',
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
                      color: '#6B7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      Ano
                    </th>
                    <th style={{
                      textAlign: 'right',
                      padding: '12px 8px',
                      fontSize: '11px',
                      fontWeight: '700',
                      color: '#6B7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      Contratos
                    </th>
                    <th style={{
                      textAlign: 'right',
                      padding: '12px 8px',
                      fontSize: '11px',
                      fontWeight: '700',
                      color: '#6B7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      Executado
                    </th>
                    <th style={{
                      textAlign: 'right',
                      padding: '12px 8px',
                      fontSize: '11px',
                      fontWeight: '700',
                      color: '#6B7280',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px'
                    }}>
                      Ticket Médio
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {data.historico.map((ano, index) => (
                    <tr
                      key={ano.ano}
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
                        color: '#1A1A1A'
                      }}>
                        {ano.ano}
                      </td>
                      <td style={{
                        padding: '12px 8px',
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#1A1A1A',
                        textAlign: 'right'
                      }}>
                        {formatters.number(ano.contratos)}
                      </td>
                      <td style={{
                        padding: '12px 8px',
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#1A1A1A',
                        textAlign: 'right'
                      }}>
                        {formatters.currency(ano.valorExecutado)}
                      </td>
                      <td style={{
                        padding: '12px 8px',
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#1A1A1A',
                        textAlign: 'right'
                      }}>
                        {formatters.currency(ano.ticketMedio)}
                      </td>
                    </tr>
                  ))}
                  {/* Linha de Média */}
                  <tr style={{
                    backgroundColor: colors.light,
                    borderTop: '2px solid ' + colors.border
                  }}>
                    <td style={{
                      padding: '12px 8px',
                      fontSize: '14px',
                      fontWeight: '700',
                      color: colors.text
                    }}>
                      Média
                    </td>
                    <td style={{
                      padding: '12px 8px',
                      fontSize: '14px',
                      fontWeight: '700',
                      color: colors.text,
                      textAlign: 'right'
                    }}>
                      {formatters.number(data.contratos.mediaAnual)}
                    </td>
                    <td style={{
                      padding: '12px 8px',
                      fontSize: '14px',
                      fontWeight: '700',
                      color: colors.text,
                      textAlign: 'right'
                    }}>
                      {formatters.currency(data.orcamento.total)}
                    </td>
                    <td style={{
                      padding: '12px 8px',
                      fontSize: '14px',
                      fontWeight: '700',
                      color: colors.text,
                      textAlign: 'right'
                    }}>
                      {formatters.currency(Math.round(data.orcamento.total / data.contratos.mediaAnual))}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* CTAs */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <button style={{
            flex: 1,
            padding: '16px 24px',
            borderRadius: '12px',
            fontWeight: '700',
            color: '#FFFFFF',
            background: colors.gradient,
            border: 'none',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            fontSize: '14px',
            transition: 'all 0.2s'
          }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2)';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            <span>✨</span>
            <span>Ver Editais ({formatters.number(data.oportunidades.editaisAtivos)})</span>
          </button>
          <button style={{
            backgroundColor: '#FFFFFF',
            border: '2px solid #E5E7EB',
            padding: '16px 24px',
            borderRadius: '12px',
            fontWeight: '700',
            color: '#1A1A1A',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            fontSize: '14px',
            transition: 'all 0.2s'
          }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#D1D5DB';
              e.currentTarget.style.backgroundColor = '#F9FAFB';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#E5E7EB';
              e.currentTarget.style.backgroundColor = '#FFFFFF';
            }}
          >
            <span>📥</span>
            <span>Exportar</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// Componentes auxiliares
const MetricBox: React.FC<{ label: string; value: string; subtitle: string }> = ({ label, value, subtitle }) => (
  <div style={{
    backgroundColor: '#F7F7F7',
    padding: '20px',
    borderRadius: '12px',
    textAlign: 'center',
    border: '2px solid #E5E7EB',
    transition: 'all 0.2s'
  }}
    onMouseEnter={(e) => {
      e.currentTarget.style.borderColor = '#10b981';
      e.currentTarget.style.transform = 'scale(1.05)';
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.borderColor = '#E5E7EB';
      e.currentTarget.style.transform = 'scale(1)';
    }}
  >
    <div style={{
      fontSize: '11px',
      fontWeight: '700',
      color: '#6B7280',
      textTransform: 'uppercase',
      marginBottom: '8px'
    }}>
      {label}
    </div>
    <div style={{
      fontSize: '24px',
      fontWeight: '700',
      color: '#1A1A1A',
      marginBottom: '4px'
    }}>
      {value}
    </div>
    <div style={{
      fontSize: '12px',
      color: '#6B7280',
      fontWeight: '600'
    }}>
      {subtitle}
    </div>
  </div>
);

const OppBox: React.FC<{ label: string; value: string; subtitle: string }> = ({ label, value, subtitle }) => (
  <div style={{
    background: 'linear-gradient(to bottom right, #FEF3C7, #FDE68A)',
    padding: '16px',
    borderRadius: '12px',
    border: '2px solid #FCD34D'
  }}>
    <div style={{
      fontSize: '11px',
      fontWeight: '700',
      color: '#78350F',
      textTransform: 'uppercase',
      marginBottom: '6px'
    }}>
      {label}
    </div>
    <div style={{
      fontSize: '20px',
      fontWeight: '700',
      color: '#1A1A1A',
      marginBottom: '2px'
    }}>
      {value}
    </div>
    <div style={{
      fontSize: '12px',
      color: '#78350F',
      fontWeight: '600'
    }}>
      {subtitle}
    </div>
  </div>
);

const CompBox: React.FC<{ label: string; value: string; diff: string }> = ({ label, value, diff }) => (
  <div style={{
    backgroundColor: '#F7F7F7',
    padding: '16px',
    borderRadius: '12px',
    border: '2px solid #E5E7EB'
  }}>
    <div style={{
      fontSize: '11px',
      fontWeight: '700',
      color: '#6B7280',
      textTransform: 'uppercase',
      marginBottom: '8px'
    }}>
      {label}
    </div>
    <div style={{
      fontSize: '18px',
      fontWeight: '700',
      color: '#1A1A1A',
      marginBottom: '8px'
    }}>
      {value}
    </div>
    <div style={{
      fontSize: '13px',
      fontWeight: '700',
      color: '#92400E',
      backgroundColor: '#FEF3C7',
      padding: '4px 12px',
      borderRadius: '6px',
      display: 'inline-block'
    }}>
      {diff}
    </div>
  </div>
);

export default OportunidadeCard;
