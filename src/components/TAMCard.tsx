import React, { useState, useEffect } from 'react';

// Tipos para configuração do TAM
export type BudgetType = 'total' | 'variable' | 'fixed';
export type EducationStage = 'infantil' | 'fundamental' | 'medio' | 'superior';

interface TAMConfig {
  budgetType: BudgetType;
  stages: EducationStage[];
}

interface TAMCardProps {
  region?: string;
  onCalculate?: (config: TAMConfig) => number;
  initialValue?: number;
  mockData?: {
    total: { total: number; variable: number; fixed: number };
    infantil: { total: number; variable: number; fixed: number };
    fundamental: { total: number; variable: number; fixed: number };
    medio: { total: number; variable: number; fixed: number };
    superior: { total: number; variable: number; fixed: number };
  };
  onOpenAdvancedFilters?: () => void;
}

const TAMCard: React.FC<TAMCardProps> = ({
  region = 'Brasil',
  onCalculate,
  initialValue = 89500000000,
  mockData = {
    total: { total: 89500000000, variable: 67125000000, fixed: 22375000000 },
    infantil: { total: 22375000000, variable: 16781250000, fixed: 5593750000 },
    fundamental: { total: 35800000000, variable: 26850000000, fixed: 8950000000 },
    medio: { total: 17900000000, variable: 13425000000, fixed: 4475000000 },
    superior: { total: 13425000000, variable: 10068750000, fixed: 3356250000 },
  },
  onOpenAdvancedFilters
}) => {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [config, setConfig] = useState<TAMConfig>({
    budgetType: 'variable',
    stages: ['infantil', 'fundamental', 'medio', 'superior']
  });
  const [tamValue, setTamValue] = useState(initialValue);
  const [isAnimating, setIsAnimating] = useState(false);

  // Nomes das etapas
  const stageNames: Record<EducationStage, string> = {
    infantil: 'Educação Infantil',
    fundamental: 'Ensino Fundamental',
    medio: 'Ensino Médio',
    superior: 'Ensino Superior'
  };

  // Nomes dos tipos de orçamento
  const budgetTypeNames: Record<BudgetType, string> = {
    total: 'Orçamento Total',
    variable: 'Orçamento Variável',
    fixed: 'Orçamento Fixo'
  };

  // Legendas para cada tipo de orçamento
  const budgetLegends: Record<BudgetType, string> = {
    total: 'Recursos totais disponíveis para educação no mercado.',
    variable: 'Recursos com flexibilidade para contratação de produtos e serviços educacionais.',
    fixed: 'Recursos comprometidos com despesas fixas e obrigatórias.'
  };

  // Calcula o TAM baseado na configuração
  const calculateTAM = (newConfig: TAMConfig): number => {
    if (onCalculate) {
      return onCalculate(newConfig);
    }

    // Lógica de cálculo padrão usando mock data
    let total = 0;

    if (newConfig.stages.length === 4) {
      // Todas as etapas = usar total
      total = mockData.total[newConfig.budgetType];
    } else {
      // Somar apenas as etapas selecionadas
      newConfig.stages.forEach(stage => {
        total += mockData[stage][newConfig.budgetType];
      });
    }

    return total;
  };

  // Atualiza o TAM quando a config mudar
  useEffect(() => {
    const newValue = calculateTAM(config);
    setIsAnimating(true);
    setTamValue(newValue);

    const timer = setTimeout(() => setIsAnimating(false), 500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config]);

  // Formata o valor em bilhões
  const formatTAM = (value: number): string => {
    const billions = value / 1000000000;
    return `R$ ${billions.toFixed(1)} bi`;
  };

  // Aplica configuração
  const handleApply = () => {
    setIsPanelOpen(false);
  };

  // Restaura padrão
  const handleRestore = () => {
    setConfig({
      budgetType: 'variable',
      stages: ['infantil', 'fundamental', 'medio', 'superior']
    });
  };

  // Toggle de etapa
  const toggleStage = (stage: EducationStage) => {
    setConfig(prev => ({
      ...prev,
      stages: prev.stages.includes(stage)
        ? prev.stages.filter(s => s !== stage)
        : [...prev.stages, stage]
    }));
  };

  // Muda tipo de orçamento
  const handleBudgetTypeChange = (type: BudgetType) => {
    setConfig(prev => ({
      ...prev,
      budgetType: type
    }));
  };

  return (
    <div style={{
      position: 'relative',
      width: '304px',
      minHeight: '320px',
    }}>
      {/* Card Principal */}
      <div style={{
        background: 'linear-gradient(135deg, #8725FF 0%, #6B1FD4 100%)',
        borderRadius: '16px',
        padding: '18px 14px',
        boxShadow: '0px 4px 16px 0px rgba(135, 37, 255, 0.2)',
        color: '#FFFFFF',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '12px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '18px'
            }}>
              💰
            </div>
            <div style={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 700,
              fontSize: '13px',
              lineHeight: '1.2',
              letterSpacing: '0.3px'
            }}>
              TAMANHO DE<br/>MERCADO (TAM)
            </div>
          </div>

          {/* Ícone de info com tooltip */}
          <div
            style={{
              cursor: 'help',
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px'
            }}
            title="O TAM responde apenas aos parâmetros de cálculo definidos neste card, não aos filtros gerais da plataforma."
          >
            ❓
          </div>
        </div>

        {/* Botões de Tipo de Orçamento */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '6px',
          marginBottom: '12px',
        }}>
          {/* Orçamento Total */}
          <button
            onClick={() => handleBudgetTypeChange('total')}
            style={{
              padding: '10px 6px',
              borderRadius: '8px',
              border: config.budgetType === 'total' ? '2px solid #FFFFFF' : '1px solid rgba(255, 255, 255, 0.3)',
              background: config.budgetType === 'total' ? '#FFFFFF' : 'rgba(255, 255, 255, 0.1)',
              color: config.budgetType === 'total' ? '#8725FF' : '#FFFFFF',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              textAlign: 'center',
              fontWeight: 600,
              fontSize: '11px',
              lineHeight: '1.2',
              boxShadow: config.budgetType === 'total' ? '0 2px 8px rgba(255, 255, 255, 0.3)' : 'none'
            }}
            onMouseEnter={(e) => {
              if (config.budgetType !== 'total') {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
              }
            }}
            onMouseLeave={(e) => {
              if (config.budgetType !== 'total') {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              }
            }}
          >
            <div style={{ marginBottom: '2px', fontSize: '10px' }}>Orçamento</div>
            <div style={{ fontWeight: 700, fontSize: '12px' }}>Total</div>
          </button>

          {/* Orçamento Variável */}
          <button
            onClick={() => handleBudgetTypeChange('variable')}
            style={{
              padding: '10px 6px',
              borderRadius: '8px',
              border: config.budgetType === 'variable' ? '2px solid #FFFFFF' : '1px solid rgba(255, 255, 255, 0.3)',
              background: config.budgetType === 'variable' ? '#FFFFFF' : 'rgba(255, 255, 255, 0.1)',
              color: config.budgetType === 'variable' ? '#8725FF' : '#FFFFFF',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              textAlign: 'center',
              fontWeight: 600,
              fontSize: '11px',
              lineHeight: '1.2',
              boxShadow: config.budgetType === 'variable' ? '0 2px 8px rgba(255, 255, 255, 0.3)' : 'none'
            }}
            onMouseEnter={(e) => {
              if (config.budgetType !== 'variable') {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
              }
            }}
            onMouseLeave={(e) => {
              if (config.budgetType !== 'variable') {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              }
            }}
          >
            <div style={{ marginBottom: '2px', fontSize: '10px' }}>Orçamento</div>
            <div style={{ fontWeight: 700, fontSize: '12px' }}>Variável</div>
          </button>

          {/* Orçamento Fixo */}
          <button
            onClick={() => handleBudgetTypeChange('fixed')}
            style={{
              padding: '10px 6px',
              borderRadius: '8px',
              border: config.budgetType === 'fixed' ? '2px solid #FFFFFF' : '1px solid rgba(255, 255, 255, 0.3)',
              background: config.budgetType === 'fixed' ? '#FFFFFF' : 'rgba(255, 255, 255, 0.1)',
              color: config.budgetType === 'fixed' ? '#8725FF' : '#FFFFFF',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              textAlign: 'center',
              fontWeight: 600,
              fontSize: '11px',
              lineHeight: '1.2',
              boxShadow: config.budgetType === 'fixed' ? '0 2px 8px rgba(255, 255, 255, 0.3)' : 'none'
            }}
            onMouseEnter={(e) => {
              if (config.budgetType !== 'fixed') {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
              }
            }}
            onMouseLeave={(e) => {
              if (config.budgetType !== 'fixed') {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
              }
            }}
          >
            <div style={{ marginBottom: '2px', fontSize: '10px' }}>Orçamento</div>
            <div style={{ fontWeight: 700, fontSize: '12px' }}>Fixo</div>
          </button>
        </div>

        {/* Card de dados */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.15)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '12px',
          padding: '14px 12px',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
        }}>
          {/* Região */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <div style={{
              background: '#FFFFFF',
              padding: '4px',
              borderRadius: '6px',
              fontSize: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              🌎
            </div>
            <div style={{
              fontFamily: 'Inter, sans-serif',
              fontWeight: 700,
              fontSize: '18px'
            }}>
              {region}
            </div>
          </div>

          {/* Valor com animação */}
          <div style={{
            fontFamily: 'Inter, sans-serif',
            fontWeight: 900,
            fontSize: '28px',
            transition: 'opacity 0.3s',
            opacity: isAnimating ? 0.5 : 1,
            letterSpacing: '-0.5px'
          }}>
            {formatTAM(tamValue)}
          </div>

          {/* Legenda explicativa */}
          <div style={{
            fontSize: '10px',
            lineHeight: '1.3',
            color: 'rgba(255, 255, 255, 0.9)',
            padding: '8px 10px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '6px',
            borderLeft: '2px solid #FFFFFF'
          }}>
            {budgetLegends[config.budgetType]}
          </div>
        </div>

        {/* Link de Configurações Avançadas */}
        <button
          onClick={() => {
            if (onOpenAdvancedFilters) {
              onOpenAdvancedFilters();
            } else {
              setIsPanelOpen(!isPanelOpen);
            }
          }}
          style={{
            width: '100%',
            marginTop: '10px',
            padding: '7px',
            borderRadius: '8px',
            border: 'none',
            background: 'rgba(255, 255, 255, 0.1)',
            color: '#FFFFFF',
            cursor: 'pointer',
            fontSize: '10px',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '5px',
            transition: 'all 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.15)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.1)';
          }}
        >
          <span>⚙️</span>
          <span>Configurações Avançadas {!onOpenAdvancedFilters && isPanelOpen ? '▲' : '▼'}</span>
        </button>
      </div>

      {/* Painel de Ajuste Avançado - só mostra se não tiver função externa */}
      {!onOpenAdvancedFilters && isPanelOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          marginTop: '8px',
          background: '#FFFFFF',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)',
          padding: '16px',
          zIndex: 1000,
          animation: 'slideDown 0.2s ease-out',
        }}>
          {/* Título do painel */}
          <h3 style={{
            margin: '0 0 12px 0',
            fontSize: '13px',
            fontWeight: 700,
            color: '#2e3138'
          }}>
            Filtrar por etapas educacionais
          </h3>

          {/* Etapas Educacionais */}
          <div style={{ marginBottom: '16px' }}>
            {(['infantil', 'fundamental', 'medio', 'superior'] as EducationStage[]).map((stage) => (
              <label
                key={stage}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px',
                  cursor: 'pointer',
                  borderRadius: '6px',
                  marginBottom: '4px',
                  background: config.stages.includes(stage) ? '#F7F3FF' : 'transparent',
                  transition: 'background 0.2s'
                }}
                onMouseEnter={(e) => {
                  if (!config.stages.includes(stage)) {
                    e.currentTarget.style.background = '#F9F9F9';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!config.stages.includes(stage)) {
                    e.currentTarget.style.background = 'transparent';
                  }
                }}
              >
                <input
                  type="checkbox"
                  checked={config.stages.includes(stage)}
                  onChange={() => toggleStage(stage)}
                  style={{ cursor: 'pointer' }}
                />
                <span style={{
                  fontSize: '13px',
                  color: '#2e3138',
                  fontWeight: config.stages.includes(stage) ? 600 : 400
                }}>
                  {stageNames[stage]}
                </span>
              </label>
            ))}
          </div>

          {/* Botões */}
          <div style={{
            display: 'flex',
            gap: '8px',
            marginTop: '12px'
          }}>
            <button
              onClick={handleApply}
              style={{
                flex: 1,
                padding: '10px',
                background: '#8725FF',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#6B1FD4';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#8725FF';
              }}
            >
              Aplicar
            </button>

            <button
              onClick={handleRestore}
              style={{
                flex: 1,
                padding: '10px',
                background: 'transparent',
                color: '#5219a1',
                border: '1px solid #8725FF',
                borderRadius: '8px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#F7F3FF';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
              }}
            >
              Restaurar padrão
            </button>
          </div>
        </div>
      )}

      {/* Overlay para fechar o painel */}
      {isPanelOpen && (
        <div
          onClick={() => setIsPanelOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 999
          }}
        />
      )}

      {/* Animação de slide down */}
      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default TAMCard;
