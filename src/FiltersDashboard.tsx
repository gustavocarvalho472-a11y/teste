import React, { useState } from 'react';
import TAMCard from './components/TAMCard';
import FinancialTotalizers from './components/FinancialTotalizers';

type FilterChip = {
  id: string;
  label: string;
};

const initialExternalFilters: FilterChip[] = [
  { id: 'region', label: 'Região: Selecionada' },
  { id: 'year', label: 'Ano: Selecionado' }
];

const educationSegments = [
  { id: 'todos', label: 'Todos', icon: '🎓' },
  { id: 'fundamental', label: 'Ensino fundamental' },
  { id: 'basico', label: 'Ensino Básico' },
  { id: 'medio', label: 'Ensino Médio' },
  { id: 'superior', label: 'Ensino Superior' }
];

const vaarStatuses = [
  { id: 'todos', label: 'Todos', icon: '🪙' },
  { id: 'habilitados', label: 'Habilitados' },
  { id: 'nao-habilitados', label: 'Não Habilitados' }
];

const networkSegmentations = [
  {
    id: 'grandes-redes',
    label: 'Grandes Redes',
    description: 'Alta em matrículas, Alto ou Baixo em VAAT'
  },
  {
    id: 'baixa-capacidade',
    label: 'Redes de Baixa Capacidade Orçamentária',
    description: 'Médio ou Baixo em matrículas, Baixo em VAAT'
  },
  {
    id: 'intermediarias',
    label: 'Redes Intermediárias',
    description: 'Médio ou Baixo em matrículas, Alto em VAAT'
  }
];

const archetypeOptions = [
  { id: 'AA', label: 'AA', description: 'Alto / Alto' },
  { id: 'AB', label: 'AB', description: 'Alto / Baixo' },
  { id: 'MA', label: 'MA', description: 'Médio / Alto' },
  { id: 'MB', label: 'MB', description: 'Médio / Baixo' },
  { id: 'BA', label: 'BA', description: 'Baixo / Alto' },
  { id: 'BB', label: 'BB', description: 'Baixo / Baixo' }
];

const FiltersDashboard: React.FC = () => {
  const [activeFilters, setActiveFilters] = useState<FilterChip[]>(initialExternalFilters);
  const [educationSegment, setEducationSegment] = useState<string>('medio');
  const [vaarStatus, setVaarStatus] = useState<string>('todos');
  const [selectedNetworkSegments, setSelectedNetworkSegments] = useState<string[]>([]);
  const [selectedArchetypes, setSelectedArchetypes] = useState<string[]>([]);

  const updateFilterChip = (id: string, label: string, isActive: boolean) => {
    setActiveFilters(prev => {
      if (isActive) {
        const exists = prev.some(chip => chip.id === id);
        const nextChip = { id, label };
        return exists
          ? prev.map(chip => (chip.id === id ? nextChip : chip))
          : [...prev, nextChip];
      }
      return prev.filter(chip => chip.id !== id);
    });
  };

  const handleEducationChange = (id: string) => {
    setEducationSegment(id);
    const selected = educationSegments.find(option => option.id === id);
    if (id === 'todos' || !selected) {
      updateFilterChip('education', '', false);
    } else {
      updateFilterChip('education', `Segmento: ${selected.label}`, true);
    }
  };

  const handleVaarChange = (id: string) => {
    setVaarStatus(id);
    const selected = vaarStatuses.find(option => option.id === id);
    if (id === 'todos' || !selected) {
      updateFilterChip('vaar', '', false);
    } else {
      updateFilterChip('vaar', `VAAR: ${selected.label}`, true);
    }
  };

  const handleNetworkToggle = (id: string) => {
    setSelectedNetworkSegments(prev => {
      const exists = prev.includes(id);
      const next = exists ? prev.filter(item => item !== id) : [...prev, id];
      if (next.length === 0) {
        updateFilterChip('network', '', false);
      } else {
        const display = next
          .map(item => networkSegmentations.find(option => option.id === item)?.label)
          .filter(Boolean)
          .join(', ');
        updateFilterChip('network', `Segmentação: ${display}`, true);
      }
      return next;
    });
  };

  const handleArchetypeToggle = (id: string) => {
    setSelectedArchetypes(prev => {
      const exists = prev.includes(id);
      const next = exists ? prev.filter(item => item !== id) : [...prev, id];
      if (next.length === 0) {
        updateFilterChip('archetype', '', false);
      } else {
        updateFilterChip('archetype', `Arquétipos: ${next.join(', ')}`, true);
      }
      return next;
    });
  };

  const handleRemoveFilter = (id: string) => {
    setActiveFilters(prev => prev.filter(chip => chip.id !== id));
    if (id === 'education') {
      setEducationSegment('todos');
    }
    if (id === 'vaar') {
      setVaarStatus('todos');
    }
    if (id === 'network') {
      setSelectedNetworkSegments([]);
    }
    if (id === 'archetype') {
      setSelectedArchetypes([]);
    }
  };

  const handleClearAll = () => {
    setEducationSegment('todos');
    setVaarStatus('todos');
    setSelectedNetworkSegments([]);
    setSelectedArchetypes([]);
    setActiveFilters(initialExternalFilters);
  };

  const handleApply = () => {
    const payload = {
      educationSegment,
      vaarStatus,
      networkSegments: selectedNetworkSegments,
      archetypes: selectedArchetypes
    };
    // Exibe no console para que o dev consiga validar rapidamente.
    // eslint-disable-next-line no-console
    console.log('Aplicar filtros', payload);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#F6F6FB', padding: '32px 24px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <header style={{ marginBottom: '24px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#1F2937', marginBottom: '8px' }}>
            Configuração de filtros
          </h1>
          <p style={{ color: '#6B7280', fontSize: '15px' }}>
            Ajuste o funil de análise para refinar os resultados do painel.
          </p>
        </header>

        <div
          style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '20px',
            padding: '28px',
            boxShadow: '0 12px 30px rgba(30, 64, 175, 0.08)',
            border: '1px solid #E5E7EB'
          }}
        >
          <section style={{ marginBottom: '24px' }}>
            <div style={{ color: '#6B7280', fontSize: '13px', fontWeight: 600, marginBottom: '12px' }}>
              Filtros ativos:
            </div>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              {activeFilters.map(chip => (
                <button
                  key={chip.id}
                  onClick={() => handleRemoveFilter(chip.id)}
                  type="button"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 14px',
                    borderRadius: '999px',
                    border: '1px solid #D1D5DB',
                    backgroundColor: '#F9FAFB',
                    color: '#374151',
                    fontSize: '13px',
                    cursor: 'pointer'
                  }}
                >
                  <span>{chip.label}</span>
                  <span style={{ color: '#9CA3AF', fontSize: '16px', lineHeight: 1 }}>×</span>
                </button>
              ))}
            </div>
          </section>

          {/* Nova Seção: TAM + Totalizadores lado a lado */}
          <section style={{ marginBottom: '32px' }}>
            <div style={{
              display: 'grid',
              gridTemplateColumns: '320px 1fr',
              gap: '20px',
              alignItems: 'start'
            }}>
              {/* Coluna Esquerda: TAM Card */}
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '12px'
                }}>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: 700,
                    color: '#1F2937'
                  }}>
                    💰 TAMANHO DE MERCADO (TAM)
                  </div>
                  <span style={{
                    fontSize: '10px',
                    color: '#6B7280',
                    backgroundColor: '#FEF3C7',
                    padding: '3px 8px',
                    borderRadius: '999px',
                    fontWeight: 600,
                    border: '1px solid #FCD34D'
                  }}>
                    ⚠️ Independente
                  </span>
                </div>
                <TAMCard />
              </div>

              {/* Coluna Direita: Totalizadores Financeiros */}
              <FinancialTotalizers />
            </div>
          </section>

          <section
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 0.8fr)',
              gap: '20px',
              marginBottom: '32px'
            }}
          >
            <div
              style={{
                border: '1px solid #E5E7EB',
                borderRadius: '16px',
                backgroundColor: '#FBFBFF',
                padding: '20px'
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '16px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '12px',
                      background: 'linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '18px'
                    }}
                  >
                    🎓
                  </div>
                  <div>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#1F2937' }}>
                      Segmento de educação
                    </div>
                    <div style={{ fontSize: '13px', color: '#6B7280' }}>Selecione um segmento</div>
                  </div>
                </div>
                <span style={{ color: '#9CA3AF', fontSize: '18px' }}>▲</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {educationSegments.map(option => {
                  const isSelected = educationSegment === option.id;
                  return (
                    <button
                      key={option.id}
                      type="button"
                      onClick={() => handleEducationChange(option.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: option.id === 'todos' ? '12px 14px' : '12px 16px',
                        borderRadius: '12px',
                        border: isSelected ? '2px solid #6366F1' : '1px solid transparent',
                        backgroundColor: isSelected ? '#EEF2FF' : '#FFFFFF',
                        color: isSelected ? '#312E81' : '#4B5563',
                        fontSize: '14px',
                        fontWeight: isSelected ? 600 : 500,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        boxShadow: isSelected ? '0 4px 12px rgba(99, 102, 241, 0.15)' : 'none'
                      }}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {option.icon && <span style={{ fontSize: '16px' }}>{option.icon}</span>}
                        {option.label}
                      </span>
                      {isSelected && <span style={{ fontSize: '16px' }}>•</span>}
                    </button>
                  );
                })}
              </div>
            </div>

            <div
              style={{
                border: '1px solid #E5E7EB',
                borderRadius: '16px',
                backgroundColor: '#FBFBFF',
                padding: '20px'
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '16px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '12px',
                      background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '18px'
                    }}
                  >
                    🪙
                  </div>
                  <div>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#1F2937' }}>
                      Habilitados para o VAAR (Cond III)
                    </div>
                    <div style={{ fontSize: '13px', color: '#6B7280' }}>Defina a elegibilidade</div>
                  </div>
                </div>
                <span style={{ color: '#9CA3AF', fontSize: '18px' }}>▲</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {vaarStatuses.map(option => {
                  const isSelected = vaarStatus === option.id;
                  return (
                    <button
                      key={option.id}
                      type="button"
                      onClick={() => handleVaarChange(option.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        border: isSelected ? '2px solid #10B981' : '1px solid transparent',
                        backgroundColor: isSelected ? '#ECFDF5' : '#FFFFFF',
                        color: isSelected ? '#047857' : '#4B5563',
                        fontSize: '14px',
                        fontWeight: isSelected ? 600 : 500,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        boxShadow: isSelected ? '0 4px 12px rgba(16, 185, 129, 0.2)' : 'none'
                      }}
                    >
                      <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {option.icon && <span style={{ fontSize: '16px' }}>{option.icon}</span>}
                        {option.label}
                      </span>
                      {isSelected && <span style={{ fontSize: '16px' }}>•</span>}
                    </button>
                  );
                })}
              </div>
            </div>
          </section>

          <section style={{ marginBottom: '24px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#7C3AED', marginBottom: '16px' }}>
              FILTROS AVANÇADOS
            </div>

            <div
              style={{
                border: '1px solid #E5E7EB',
                borderRadius: '16px',
                padding: '20px',
                backgroundColor: '#FFFFFF',
                marginBottom: '16px'
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '20px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '18px' }}>🌀</span>
                  <div>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#1F2937' }}>
                      Segmentação de Rede
                    </div>
                    <div style={{ fontSize: '13px', color: '#6B7280' }}>
                      Escolha agrupamentos estratégicos
                    </div>
                  </div>
                </div>
                <span style={{ color: '#9CA3AF', fontSize: '18px' }}>▲</span>
              </div>

              <div style={{ display: 'grid', gap: '12px' }}>
                {networkSegmentations.map(option => {
                  const isSelected = selectedNetworkSegments.includes(option.id);
                  return (
                    <button
                      key={option.id}
                      type="button"
                      onClick={() => handleNetworkToggle(option.id)}
                      aria-pressed={isSelected}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '14px',
                        padding: '16px',
                        borderRadius: '14px',
                        border: isSelected ? '2px solid #6366F1' : '1px solid #E5E7EB',
                        backgroundColor: isSelected ? '#EEF2FF' : '#F9FAFB',
                        color: '#1F2937',
                        textAlign: 'left',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <span
                        style={{
                          width: '20px',
                          height: '20px',
                          borderRadius: '6px',
                          border: isSelected ? '6px solid #6366F1' : '2px solid #D1D5DB',
                          backgroundColor: isSelected ? '#6366F1' : '#FFFFFF',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#FFFFFF',
                          fontSize: '12px',
                          transition: 'all 0.2s ease'
                        }}
                      >
                        {isSelected ? '✓' : ''}
                      </span>
                      <span>
                        <div style={{ fontWeight: 600, marginBottom: '6px' }}>{option.label}</div>
                        <div style={{ fontSize: '13px', color: '#6B7280' }}>{option.description}</div>
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            <div
              style={{
                border: '1px solid #E5E7EB',
                borderRadius: '16px',
                padding: '20px',
                backgroundColor: '#FFFFFF'
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '20px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '18px' }}>🧩</span>
                  <div>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: '#1F2937' }}>
                      Arquétipos de Rede (Detalhado)
                    </div>
                    <div style={{ fontSize: '13px', color: '#6B7280' }}>Selecione combinações de desempenho</div>
                  </div>
                </div>
                <span style={{ color: '#9CA3AF', fontSize: '18px' }}>▲</span>
              </div>

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                  gap: '12px'
                }}
              >
                {archetypeOptions.map(option => {
                  const isSelected = selectedArchetypes.includes(option.id);
                  return (
                    <button
                      key={option.id}
                      type='button'
                      onClick={() => handleArchetypeToggle(option.id)}
                      aria-pressed={isSelected}
                      style={{
                        borderRadius: '12px',
                        border: isSelected ? '2px solid #7C3AED' : '1px solid #E5E7EB',
                        backgroundColor: isSelected ? '#F3E8FF' : '#F9FAFB',
                        padding: '16px 12px',
                        textAlign: 'left',
                        cursor: 'pointer',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      <span style={{ fontSize: '16px', fontWeight: 700, color: '#1F2937' }}>
                        {option.label}
                      </span>
                      <span style={{ fontSize: '13px', color: '#6B7280' }}>{option.description}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </section>

          <footer
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: '32px'
            }}
          >
            <button
              type="button"
              onClick={handleClearAll}
              style={{
                background: 'none',
                border: 'none',
                color: '#6366F1',
                fontWeight: 600,
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Limpar
            </button>

            <button
              type="button"
              onClick={handleApply}
              style={{
                padding: '12px 32px',
                borderRadius: '999px',
                border: 'none',
                backgroundColor: '#34D399',
                color: '#FFFFFF',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: '0 12px 24px rgba(52, 211, 153, 0.3)'
              }}
            >
              Aplicar filtros
            </button>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default FiltersDashboard;
