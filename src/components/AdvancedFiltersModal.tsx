import React, { useState } from 'react';

interface AdvancedFiltersModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApply: (filters: any) => void;
}

const AdvancedFiltersModal: React.FC<AdvancedFiltersModalProps> = ({ isOpen, onClose, onApply }) => {
  const [selectedEducationSegment, setSelectedEducationSegment] = useState<string[]>(['Ensino Fundamental']);
  const [selectedNetworkSegments, setSelectedNetworkSegments] = useState<string[]>(['Grandes Redes']);
  const [selectedVaarEnabled, setSelectedVaarEnabled] = useState<string[]>(['Sudeste', 'Brasil']);
  const [selectedTamCalculation, setSelectedTamCalculation] = useState({
    type: 'Orçamento Variável',
    stages: ['Educação Infantil', 'Orçamento Fixo', 'Orçamento Total', 'Ensino Superior']
  });

  // Estados de expansão dos dropdowns
  const [isEducationExpanded, setIsEducationExpanded] = useState(true);
  const [isNetworkExpanded, setIsNetworkExpanded] = useState(true);
  const [isVaarExpanded, setIsVaarExpanded] = useState(true);
  const [isTamExpanded, setIsTamExpanded] = useState(true);

  const educationSegments = [
    'Comunicação Social',
    'Formação de Recursos Humanos',
    'Tecnologia da Informação',
    'Educação Básica',
    'Educação Infantil',
    'Ensino Fundamental',
    'Ensino Médio',
    'Ensino Profissional',
    'Assistência a Estudante'
  ];

  const networkSegments = [
    { id: 'grandes-redes', label: 'Grandes Redes', tag: 'ALTA' },
    { id: 'baixa-capacidade', label: 'Redes de Baixa Capacidade Orçamentária', tag: 'BAIXA' },
    { id: 'intermediarias', label: 'Redes Intermediárias', tag: 'MÉDIA' }
  ];

  const vaarRegions = [
    'Sudeste',
    'Sul',
    'Norte',
    'Nordeste',
    'Centro-Oeste',
    'Brasil'
  ];

  const tamStages = [
    'Educação Infantil',
    'Orçamento Fixo',
    'Orçamento Total',
    'Ensino Superior'
  ];

  const toggleEducationSegment = (segment: string) => {
    setSelectedEducationSegment(prev =>
      prev.includes(segment)
        ? prev.filter(s => s !== segment)
        : [...prev, segment]
    );
  };

  const toggleNetworkSegment = (segment: string) => {
    setSelectedNetworkSegments(prev =>
      prev.includes(segment)
        ? prev.filter(s => s !== segment)
        : [...prev, segment]
    );
  };

  const toggleVaarRegion = (region: string) => {
    setSelectedVaarEnabled(prev =>
      prev.includes(region)
        ? prev.filter(r => r !== region)
        : [...prev, region]
    );
  };

  const toggleTamStage = (stage: string) => {
    setSelectedTamCalculation(prev => ({
      ...prev,
      stages: prev.stages.includes(stage)
        ? prev.stages.filter(s => s !== stage)
        : [...prev.stages, stage]
    }));
  };

  const handleApply = () => {
    onApply({
      educationSegment: selectedEducationSegment,
      networkSegments: selectedNetworkSegments,
      vaarEnabled: selectedVaarEnabled,
      tamCalculation: selectedTamCalculation
    });
    onClose();
  };

  const handleClear = () => {
    setSelectedEducationSegment([]);
    setSelectedNetworkSegments([]);
    setSelectedVaarEnabled([]);
    setSelectedTamCalculation({ type: 'Orçamento Variável', stages: [] });
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          zIndex: 9998,
          animation: 'fadeIn 0.2s ease-out'
        }}
      />

      {/* Modal */}
      <div style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        background: '#FFFFFF',
        borderRadius: '20px',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
        zIndex: 9999,
        maxWidth: '900px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto',
        animation: 'slideUp 0.3s ease-out'
      }}>
        {/* Header com filtros ativos */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #E5E7EB',
          display: 'flex',
          gap: '12px',
          alignItems: 'center',
          flexWrap: 'wrap'
        }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#6B7280' }}>
            Filtros ativos:
          </span>
          <div style={{
            padding: '6px 12px',
            borderRadius: '999px',
            background: '#F3F4F6',
            border: '1px solid #D1D5DB',
            fontSize: '12px',
            color: '#374151',
            fontWeight: 500
          }}>
            Região: Selecionada
          </div>
          <div style={{
            padding: '6px 12px',
            borderRadius: '999px',
            background: '#F3F4F6',
            border: '1px solid #D1D5DB',
            fontSize: '12px',
            color: '#374151',
            fontWeight: 500
          }}>
            Ano: Selecionado
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: '24px' }}>
          {/* FILTROS GERAIS */}
          <div style={{
            marginBottom: '28px'
          }}>
            {/* Título da seção */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '16px'
            }}>
              <div style={{
                fontSize: '15px',
                fontWeight: 700,
                color: '#1F2937',
                letterSpacing: '0.5px'
              }}>
                FILTROS GERAIS
              </div>
              <div style={{
                flex: 1,
                height: '1px',
                background: 'linear-gradient(to right, #D1D5DB, transparent)'
              }} />
            </div>

            {/* Grid de filtros gerais */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '20px'
            }}>
              {/* Coluna 1 */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* Segmento de educação */}
              <div style={{
                border: '1px solid #E5E7EB',
                borderRadius: '12px',
                padding: '16px',
                background: '#FAFAFA'
              }}>
                <div
                  onClick={() => setIsEducationExpanded(!isEducationExpanded)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: isEducationExpanded ? '12px' : '0',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '16px' }}>🎓</span>
                    <div>
                      <div style={{
                        fontSize: '13px',
                        fontWeight: 700,
                        color: '#1F2937'
                      }}>
                        Segmento de educação
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: '#6B7280'
                      }}>
                        Filtre múltiplos por segmento
                      </div>
                    </div>
                  </div>
                  <span style={{
                    fontSize: '18px',
                    color: '#9CA3AF',
                    transition: 'transform 0.3s',
                    transform: isEducationExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
                  }}>
                    ▼
                  </span>
                </div>

                {isEducationExpanded && (
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px',
                    maxHeight: '300px',
                    overflowY: 'auto',
                    animation: 'slideDown 0.3s ease-out'
                  }}>
                  {educationSegments.map((segment) => (
                    <label
                      key={segment}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        padding: '10px 12px',
                        borderRadius: '8px',
                        background: selectedEducationSegment.includes(segment) ? '#EEF2FF' : '#FFFFFF',
                        border: selectedEducationSegment.includes(segment) ? '1px solid #6366F1' : '1px solid #E5E7EB',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={selectedEducationSegment.includes(segment)}
                        onChange={() => toggleEducationSegment(segment)}
                        style={{
                          width: '16px',
                          height: '16px',
                          cursor: 'pointer',
                          accentColor: '#6366F1'
                        }}
                      />
                      <span style={{
                        fontSize: '13px',
                        color: '#374151',
                        fontWeight: selectedEducationSegment.includes(segment) ? 600 : 400,
                        flex: 1
                      }}>
                        {segment}
                      </span>
                      {selectedEducationSegment.includes(segment) && (
                        <span style={{ color: '#6366F1', fontSize: '16px' }}>✓</span>
                      )}
                    </label>
                  ))}
                  </div>
                )}
              </div>

              {/* Segmentação de rede */}
              <div style={{
                border: '1px solid #E5E7EB',
                borderRadius: '12px',
                padding: '16px',
                background: '#FAFAFA'
              }}>
                <div
                  onClick={() => setIsNetworkExpanded(!isNetworkExpanded)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: isNetworkExpanded ? '12px' : '0',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '16px' }}>🌐</span>
                    <div>
                      <div style={{
                        fontSize: '13px',
                        fontWeight: 700,
                        color: '#1F2937'
                      }}>
                        Segmentação de rede
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: '#6B7280'
                      }}>
                        Selecione a classificação da rede
                      </div>
                    </div>
                  </div>
                  <span style={{
                    fontSize: '18px',
                    color: '#9CA3AF',
                    transition: 'transform 0.3s',
                    transform: isNetworkExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
                  }}>
                    ▼
                  </span>
                </div>

                {isNetworkExpanded && (
                  <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                    animation: 'slideDown 0.3s ease-out'
                  }}>
                  {networkSegments.map((segment) => (
                    <label
                      key={segment.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        padding: '12px',
                        borderRadius: '8px',
                        background: selectedNetworkSegments.includes(segment.label) ? '#EEF2FF' : '#FFFFFF',
                        border: selectedNetworkSegments.includes(segment.label) ? '1px solid #8B5CF6' : '1px solid #E5E7EB',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      <input
                        type="radio"
                        name="network"
                        checked={selectedNetworkSegments.includes(segment.label)}
                        onChange={() => {
                          setSelectedNetworkSegments([segment.label]);
                        }}
                        style={{
                          width: '16px',
                          height: '16px',
                          cursor: 'pointer',
                          accentColor: '#8B5CF6'
                        }}
                      />
                      <span style={{
                        fontSize: '13px',
                        color: '#374151',
                        fontWeight: 500,
                        flex: 1
                      }}>
                        {segment.label}
                      </span>
                      <span style={{
                        fontSize: '10px',
                        fontWeight: 700,
                        padding: '4px 8px',
                        borderRadius: '6px',
                        background: segment.tag === 'ALTA' ? '#8B5CF6' : segment.tag === 'BAIXA' ? '#F59E0B' : '#6B7280',
                        color: '#FFFFFF'
                      }}>
                        {segment.tag}
                      </span>
                    </label>
                  ))}
                  <label
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '12px',
                      borderRadius: '8px',
                      background: '#FFFFFF',
                      border: '1px solid #E5E7EB',
                      cursor: 'pointer'
                    }}
                  >
                    <input
                      type="radio"
                      name="network"
                      style={{
                        width: '16px',
                        height: '16px',
                        cursor: 'pointer'
                      }}
                    />
                    <span style={{
                      fontSize: '13px',
                      color: '#374151',
                      fontWeight: 500
                    }}>
                      Todos
                    </span>
                  </label>
                  </div>
                )}
              </div>
            </div>

              {/* Coluna 2 */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* Habilitados para o VAAR */}
                <div style={{
                  border: '1px solid #E5E7EB',
                  borderRadius: '12px',
                  padding: '16px',
                  background: '#FAFAFA'
                }}>
                  <div
                    onClick={() => setIsVaarExpanded(!isVaarExpanded)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: isVaarExpanded ? '12px' : '0',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '16px' }}>💰</span>
                      <div>
                        <div style={{
                          fontSize: '13px',
                          fontWeight: 700,
                          color: '#1F2937'
                        }}>
                          Habilitados para o VAAR
                        </div>
                        <div style={{
                          fontSize: '11px',
                          color: '#6B7280'
                        }}>
                          Habilite para o programa (Cond III)
                        </div>
                      </div>
                    </div>
                    <span style={{
                      fontSize: '18px',
                      color: '#9CA3AF',
                      transition: 'transform 0.3s',
                      transform: isVaarExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
                    }}>
                      ▼
                    </span>
                  </div>

                  {isVaarExpanded && (
                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '10px',
                      animation: 'slideDown 0.3s ease-out'
                    }}>
                    {vaarRegions.map((region) => (
                      <label
                        key={region}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          padding: '10px 12px',
                          borderRadius: '8px',
                          background: selectedVaarEnabled.includes(region) ? '#ECFDF5' : '#FFFFFF',
                          border: selectedVaarEnabled.includes(region) ? '1px solid #10B981' : '1px solid #E5E7EB',
                          cursor: 'pointer',
                          transition: 'all 0.2s'
                        }}
                      >
                        <input
                          type="radio"
                          name="vaar"
                          checked={selectedVaarEnabled.includes(region)}
                          onChange={() => {
                            setSelectedVaarEnabled([region]);
                          }}
                          style={{
                            width: '16px',
                            height: '16px',
                            cursor: 'pointer',
                            accentColor: '#10B981'
                          }}
                        />
                        <span style={{
                          fontSize: '13px',
                          color: '#374151',
                          fontWeight: 500,
                          flex: 1
                        }}>
                          {region}
                        </span>
                        {selectedVaarEnabled.includes(region) && (
                          <span style={{ color: '#10B981', fontSize: '16px' }}>✓</span>
                        )}
                      </label>
                    ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* FILTROS DO TAM */}
          <div>
            {/* Título da seção */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '16px'
            }}>
              <div style={{
                fontSize: '15px',
                fontWeight: 700,
                color: '#8725FF',
                letterSpacing: '0.5px'
              }}>
                FILTROS DO TAM
              </div>
              <div style={{
                flex: 1,
                height: '1px',
                background: 'linear-gradient(to right, #C084FC, transparent)'
              }} />
              <div style={{
                fontSize: '10px',
                fontWeight: 600,
                padding: '4px 10px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #F3E8FF 0%, #E9D5FF 100%)',
                color: '#8725FF',
                border: '1px solid #E9D5FF'
              }}>
                ESPECÍFICO
              </div>
            </div>

            {/* Filtro do TAM */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr',
              gap: '20px'
            }}>
              {/* Como deseja calcular o TAAM? */}
              <div style={{
                border: '2px solid #E9D5FF',
                borderRadius: '12px',
                padding: '16px',
                background: 'linear-gradient(135deg, #FEFEFF 0%, #FAF5FF 100%)',
                position: 'relative'
              }}>
                <div
                  onClick={() => setIsTamExpanded(!isTamExpanded)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: isTamExpanded ? '12px' : '0',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '16px' }}>📊</span>
                    <div>
                      <div style={{
                        fontSize: '13px',
                        fontWeight: 700,
                        color: '#6B21A8'
                      }}>
                        Como deseja calcular o TAM?
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: '#8B5CF6'
                      }}>
                        Configuração específica do indicador TAM
                      </div>
                    </div>
                  </div>
                  <span style={{
                    fontSize: '18px',
                    color: '#9CA3AF',
                    transition: 'transform 0.3s',
                    transform: isTamExpanded ? 'rotate(180deg)' : 'rotate(0deg)'
                  }}>
                    ▼
                  </span>
                </div>

                {isTamExpanded && (
                  <>
                    <div style={{
                      background: '#FFFFFF',
                      borderRadius: '8px',
                      padding: '12px',
                      marginBottom: '12px',
                      border: '1px solid #E9D5FF',
                      animation: 'slideDown 0.3s ease-out'
                    }}>
                      <div style={{
                        fontSize: '11px',
                        color: '#8B5CF6',
                        marginBottom: '8px',
                        fontWeight: 600
                      }}>
                        Tipo do Orçamento
                      </div>
                      <div style={{
                        fontSize: '13px',
                        fontWeight: 600,
                        color: '#6B21A8',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}>
                        • {selectedTamCalculation.type}
                      </div>
                    </div>

                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px',
                      animation: 'slideDown 0.3s ease-out'
                    }}>
                  {tamStages.map((stage) => (
                    <label
                      key={stage}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        padding: '10px 12px',
                        borderRadius: '8px',
                        background: selectedTamCalculation.stages.includes(stage) ? '#F3E8FF' : '#FFFFFF',
                        border: selectedTamCalculation.stages.includes(stage) ? '1.5px solid #8725FF' : '1px solid #E5E7EB',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={selectedTamCalculation.stages.includes(stage)}
                        onChange={() => toggleTamStage(stage)}
                        style={{
                          width: '16px',
                          height: '16px',
                          cursor: 'pointer',
                          accentColor: '#8725FF'
                        }}
                      />
                      <span style={{
                        fontSize: '13px',
                        color: '#374151',
                        fontWeight: selectedTamCalculation.stages.includes(stage) ? 600 : 500,
                        flex: 1
                      }}>
                        {stage}
                      </span>
                      {selectedTamCalculation.stages.includes(stage) && (
                        <span style={{ color: '#8725FF', fontSize: '16px' }}>✓</span>
                      )}
                    </label>
                  ))}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid #E5E7EB',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: '#FAFAFA'
        }}>
          <button
            onClick={handleClear}
            style={{
              padding: '0',
              border: 'none',
              background: 'transparent',
              color: '#6B7280',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            Limpar
          </button>
          <button
            onClick={handleApply}
            style={{
              padding: '10px 24px',
              borderRadius: '8px',
              border: 'none',
              background: '#10B981',
              color: '#FFFFFF',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)'
            }}
          >
            Aplicar Filtros
          </button>
        </div>
      </div>

      {/* Animations */}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translate(-50%, -40%);
          }
          to {
            opacity: 1;
            transform: translate(-50%, -50%);
          }
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            maxHeight: 0;
          }
          to {
            opacity: 1;
            maxHeight: 1000px;
          }
        }
      `}</style>
    </>
  );
};

export default AdvancedFiltersModal;
