import React, { useState } from 'react';
import TAMCard from './components/TAMCard';
import FinancialTotalizers from './components/FinancialTotalizers';
import StatesTable from './components/StatesTable';
import AdvancedFiltersModal from './components/AdvancedFiltersModal';

const QuickViewDashboard: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState<string>('Região');
  const [selectedState, setSelectedState] = useState<string>('Estado');
  const [selectedMunicipality, setSelectedMunicipality] = useState<string>('Município');
  const [selectedMicroregion, setSelectedMicroregion] = useState<string>('Microrregião');
  const [selectedMesoregion, setSelectedMesoregion] = useState<string>('Mesorregião');
  const [selectedYear, setSelectedYear] = useState<string>('Ano');
  const [selectedPeriod, setSelectedPeriod] = useState<string>('Selecione o período');

  const [financialFilters, setFinancialFilters] = useState<string>('Financeiros');
  const [educationalFilters, setEducationalFilters] = useState<string>('Educacional');
  const [networkFilters, setNetworkFilters] = useState<string>('Demografia e Rede');

  const [isAdvancedFiltersOpen, setIsAdvancedFiltersOpen] = useState<boolean>(false);

  const handleApplyAdvancedFilters = (filters: any) => {
    console.log('Filtros avançados aplicados:', filters);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #A78BFA 0%, #8B5CF6 100%)',
      padding: '24px'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {/* Container Branco Principal */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: '20px',
          padding: '24px',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)'
        }}>
          {/* Seção de Filtros Superiores */}
          <div style={{
            background: '#F3F4F6',
            borderRadius: '16px',
            padding: '20px',
            marginBottom: '24px'
          }}>
            {/* Linha 1: Filtros Geográficos */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '12px',
              flexWrap: 'wrap'
            }}>
              {/* Ícone de filtro */}
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px'
              }}>
                📍
              </div>

              {/* Região */}
              <div style={{ position: 'relative' }}>
                <select
                  value={selectedRegion}
                  onChange={(e) => setSelectedRegion(e.target.value)}
                  style={{
                    padding: '8px 32px 8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #E5E7EB',
                    background: '#FFFFFF',
                    fontSize: '13px',
                    fontWeight: 500,
                    color: '#374151',
                    cursor: 'pointer',
                    appearance: 'none'
                  }}
                >
                  <option>Região</option>
                  <option>Sudeste</option>
                  <option>Sul</option>
                  <option>Norte</option>
                  <option>Nordeste</option>
                  <option>Centro-Oeste</option>
                </select>
                <span style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '10px',
                  color: '#8B5CF6',
                  fontWeight: 700,
                  pointerEvents: 'none'
                }}>■</span>
              </div>

              {/* Estado */}
              <div style={{ position: 'relative' }}>
                <select
                  value={selectedState}
                  onChange={(e) => setSelectedState(e.target.value)}
                  style={{
                    padding: '8px 32px 8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #E5E7EB',
                    background: '#FFFFFF',
                    fontSize: '13px',
                    fontWeight: 500,
                    color: '#374151',
                    cursor: 'pointer',
                    appearance: 'none'
                  }}
                >
                  <option>Estado</option>
                  <option>São Paulo</option>
                  <option>Rio de Janeiro</option>
                  <option>Minas Gerais</option>
                  <option>Espírito Santo</option>
                </select>
                <span style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '10px',
                  color: '#EC4899',
                  fontWeight: 700,
                  pointerEvents: 'none'
                }}>■</span>
              </div>

              {/* Mesorregião */}
              <div style={{ position: 'relative' }}>
                <select
                  value={selectedMesoregion}
                  onChange={(e) => setSelectedMesoregion(e.target.value)}
                  style={{
                    padding: '8px 32px 8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #E5E7EB',
                    background: '#FFFFFF',
                    fontSize: '13px',
                    fontWeight: 500,
                    color: '#374151',
                    cursor: 'pointer',
                    appearance: 'none'
                  }}
                >
                  <option>Mesorregião</option>
                  <option>Vale do Paraíba</option>
                  <option>Metropolitana de SP</option>
                </select>
                <span style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '10px',
                  color: '#3B82F6',
                  fontWeight: 700,
                  pointerEvents: 'none'
                }}>■</span>
              </div>

              {/* Microrregião */}
              <div style={{ position: 'relative' }}>
                <select
                  value={selectedMicroregion}
                  onChange={(e) => setSelectedMicroregion(e.target.value)}
                  style={{
                    padding: '8px 32px 8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #E5E7EB',
                    background: '#FFFFFF',
                    fontSize: '13px',
                    fontWeight: 500,
                    color: '#374151',
                    cursor: 'pointer',
                    appearance: 'none'
                  }}
                >
                  <option>Microrregião</option>
                  <option>São José dos Campos</option>
                  <option>Guarulhos</option>
                </select>
                <span style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '10px',
                  color: '#F59E0B',
                  fontWeight: 700,
                  pointerEvents: 'none'
                }}>■</span>
              </div>

              {/* Município */}
              <div style={{ position: 'relative' }}>
                <select
                  value={selectedMunicipality}
                  onChange={(e) => setSelectedMunicipality(e.target.value)}
                  style={{
                    padding: '8px 32px 8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #E5E7EB',
                    background: '#FFFFFF',
                    fontSize: '13px',
                    fontWeight: 500,
                    color: '#374151',
                    cursor: 'pointer',
                    appearance: 'none'
                  }}
                >
                  <option>Município</option>
                  <option>São Paulo</option>
                  <option>Campinas</option>
                  <option>Santos</option>
                </select>
                <span style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '10px',
                  color: '#8B5CF6',
                  fontWeight: 700,
                  pointerEvents: 'none'
                }}>■</span>
              </div>

              {/* Seleção de período */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginLeft: 'auto',
                background: '#FFFFFF',
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #E5E7EB'
              }}>
                <span style={{ fontSize: '14px' }}>📅</span>
                <span style={{ fontSize: '13px', fontWeight: 500, color: '#6B7280' }}>
                  Selecione o período
                </span>
              </div>

              {/* Ano */}
              <div style={{ position: 'relative' }}>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(e.target.value)}
                  style={{
                    padding: '8px 32px 8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #E5E7EB',
                    background: '#FFFFFF',
                    fontSize: '13px',
                    fontWeight: 500,
                    color: '#374151',
                    cursor: 'pointer',
                    appearance: 'none'
                  }}
                >
                  <option>Ano</option>
                  <option>2024</option>
                  <option>2023</option>
                  <option>2022</option>
                </select>
                <span style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '10px',
                  color: '#8B5CF6',
                  fontWeight: 700,
                  pointerEvents: 'none'
                }}>■</span>
              </div>

              {/* Semestre */}
              <div style={{ position: 'relative' }}>
                <select
                  style={{
                    padding: '8px 32px 8px 12px',
                    borderRadius: '8px',
                    border: '1px solid #E5E7EB',
                    background: '#FFFFFF',
                    fontSize: '13px',
                    fontWeight: 500,
                    color: '#374151',
                    cursor: 'pointer',
                    appearance: 'none'
                  }}
                >
                  <option>Semestre a ano</option>
                  <option>1º Semestre</option>
                  <option>2º Semestre</option>
                </select>
                <span style={{
                  position: 'absolute',
                  right: '10px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '10px',
                  color: '#8B5CF6',
                  fontWeight: 700,
                  pointerEvents: 'none'
                }}>■</span>
              </div>
            </div>

            {/* Linha 2: Filtros de Indicadores */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              flexWrap: 'wrap'
            }}>
              {/* Ícone de indicadores */}
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px'
              }}>
                📊
              </div>

              {/* Financeiros */}
              <button style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid #E5E7EB',
                background: '#FFFFFF',
                fontSize: '13px',
                fontWeight: 500,
                color: '#374151',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <span style={{ fontSize: '10px', color: '#EC4899', fontWeight: 700 }}>■</span>
                Financeiros
              </button>

              {/* Educacional */}
              <button style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid #E5E7EB',
                background: '#FFFFFF',
                fontSize: '13px',
                fontWeight: 500,
                color: '#374151',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <span style={{ fontSize: '10px', color: '#8B5CF6', fontWeight: 700 }}>■</span>
                Educacional
              </button>

              {/* Demografia e Rede */}
              <button style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid #E5E7EB',
                background: '#FFFFFF',
                fontSize: '13px',
                fontWeight: 500,
                color: '#374151',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <span style={{ fontSize: '10px', color: '#7C3AED', fontWeight: 700 }}>■</span>
                Demografia e Rede
              </button>

              {/* Filtros avançados */}
              <button
                onClick={() => setIsAdvancedFiltersOpen(true)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: '1px solid #E5E7EB',
                  background: '#FFFFFF',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: '#6B7280',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  marginLeft: 'auto'
                }}>
                <span>⚙️</span>
                Filtros avançados
              </button>

              {/* Limpar */}
              <button style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                background: 'transparent',
                fontSize: '13px',
                fontWeight: 600,
                color: '#6B7280',
                cursor: 'pointer'
              }}>
                Limpar
              </button>

              {/* Aplicar Filtros */}
              <button style={{
                padding: '8px 20px',
                borderRadius: '8px',
                border: 'none',
                background: '#10B981',
                fontSize: '13px',
                fontWeight: 600,
                color: '#FFFFFF',
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)'
              }}>
                Aplicar Filtros
              </button>

              {/* Exportar */}
              <button style={{
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #E5E7EB',
                background: '#FFFFFF',
                fontSize: '13px',
                fontWeight: 500,
                color: '#374151',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <span>💾</span>
              </button>
            </div>
          </div>

          {/* Grid: TAM + Totalizadores */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '320px 1fr',
            gap: '20px',
            marginBottom: '24px'
          }}>
            {/* TAM Card */}
            <TAMCard onOpenAdvancedFilters={() => setIsAdvancedFiltersOpen(true)} />

            {/* Totalizadores */}
            <FinancialTotalizers />
          </div>

          {/* Tabela de Estados */}
          <StatesTable />
        </div>
      </div>

      {/* Modal de Filtros Avançados */}
      <AdvancedFiltersModal
        isOpen={isAdvancedFiltersOpen}
        onClose={() => setIsAdvancedFiltersOpen(false)}
        onApply={handleApplyAdvancedFilters}
      />
    </div>
  );
};

export default QuickViewDashboard;
