import React, { useState } from 'react';

interface TotalizerCardProps {
  icon: string;
  label: string;
  value: string;
  color: string;
}

const TotalizerCard: React.FC<TotalizerCardProps> = ({ icon, label, value, color }) => {
  return (
    <div style={{
      background: '#FFFFFF',
      borderRadius: '12px',
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      border: '1px solid #E5E7EB',
      transition: 'all 0.2s ease',
      cursor: 'default',
      minWidth: '140px',
      flex: '1 1 0'
    }}>
      {/* Ícone */}
      <div style={{
        width: '36px',
        height: '36px',
        borderRadius: '8px',
        background: color,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '18px'
      }}>
        {icon}
      </div>

      {/* Label */}
      <div style={{
        fontSize: '11px',
        fontWeight: 500,
        color: '#6B7280',
        lineHeight: '1.3'
      }}>
        {label}
      </div>

      {/* Valor */}
      <div style={{
        fontSize: '20px',
        fontWeight: 800,
        color: '#1F2937',
        letterSpacing: '-0.3px'
      }}>
        {value}
      </div>
    </div>
  );
};

const FinancialTotalizers: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<number>(0);

  // Dados do carrossel - 3 páginas com 4 totalizadores cada
  const allTotalizers = [
    // Página 1 - Orçamento
    [
      {
        icon: '💰',
        label: 'Orçamento Total',
        value: 'R$ 28.5 bi',
        color: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)'
      },
      {
        icon: '💵',
        label: 'Orçamento Fixo',
        value: 'R$ 8.5 bi',
        color: 'linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%)'
      },
      {
        icon: '📊',
        label: 'Orçamento Variável',
        value: 'R$ 1.5 bi',
        color: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)'
      },
      {
        icon: '📈',
        label: 'Despesas Totais',
        value: 'R$ 28.5 bi',
        color: 'linear-gradient(135deg, #E0E7FF 0%, #C7D2FE 100%)'
      }
    ],
    // Página 2 - Execução
    [
      {
        icon: '✅',
        label: 'Execução Orçamentária',
        value: '87.3%',
        color: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)'
      },
      {
        icon: '🎯',
        label: 'Meta Atingida',
        value: '92.1%',
        color: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)'
      },
      {
        icon: '⏱️',
        label: 'Prazo Médio',
        value: '45 dias',
        color: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)'
      },
      {
        icon: '💳',
        label: 'Saldo Disponível',
        value: 'R$ 3.2 bi',
        color: 'linear-gradient(135deg, #E0E7FF 0%, #C7D2FE 100%)'
      }
    ],
    // Página 3 - Indicadores
    [
      {
        icon: '👥',
        label: 'Investimento por Aluno',
        value: 'R$ 12.4k',
        color: 'linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%)'
      },
      {
        icon: '🏫',
        label: 'Escolas Beneficiadas',
        value: '1,234',
        color: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)'
      },
      {
        icon: '📚',
        label: 'Programas Ativos',
        value: '48',
        color: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)'
      },
      {
        icon: '🌟',
        label: 'Índice de Qualidade',
        value: '8.6',
        color: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)'
      }
    ]
  ];

  const totalPages = allTotalizers.length;
  const totalizers = allTotalizers[currentPage];

  return (
    <div style={{
      background: '#FFFFFF',
      borderRadius: '16px',
      padding: '20px',
      border: '1px solid #E5E7EB',
    }}>
      {/* Header */}
      <div style={{
        marginBottom: '16px',
        paddingBottom: '12px',
        borderBottom: '1px solid #F3F4F6'
      }}>
        <div style={{
          fontSize: '15px',
          fontWeight: 700,
          color: '#1F2937',
          marginBottom: '4px'
        }}>
          Totalizadores de Indicadores Financeiros
        </div>
        <div style={{
          fontSize: '12px',
          color: '#6B7280'
        }}>
          Indicadores financeiros de educação — dados atualizados conforme os últimos relatórios, por filtros.
        </div>
      </div>

      {/* Totalizadores Grid */}
      <div
        key={currentPage}
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: '12px',
          animation: 'fadeIn 0.4s ease-in-out'
        }}
      >
        {totalizers.map((totalizer, index) => (
          <TotalizerCard
            key={index}
            icon={totalizer.icon}
            label={totalizer.label}
            value={totalizer.value}
            color={totalizer.color}
          />
        ))}
      </div>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateX(10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>

      {/* Indicador de navegação */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        gap: '8px',
        marginTop: '16px'
      }}>
        {Array.from({ length: totalPages }).map((_, index) => (
          <div
            key={index}
            onClick={() => setCurrentPage(index)}
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: currentPage === index ? '#8725FF' : '#D1D5DB',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              transform: currentPage === index ? 'scale(1.2)' : 'scale(1)'
            }}
            onMouseEnter={(e) => {
              if (currentPage !== index) {
                e.currentTarget.style.background = '#9CA3AF';
              }
            }}
            onMouseLeave={(e) => {
              if (currentPage !== index) {
                e.currentTarget.style.background = '#D1D5DB';
              }
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default FinancialTotalizers;
