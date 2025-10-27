import React from 'react';

interface StateData {
  id: string;
  name: string;
  totalBudget: string;
  fixedBudget: string;
  variableBudget: string;
  totalExpenses: string;
  fixedExpenses: string;
  variableExpenses: string;
  disposableValue: string;
  ides: number;
  idesBasicEd: number;
  idesHighSchool: number;
  idesAverage: number;
  saebScore: number;
}

const StatesTable: React.FC = () => {
  const states: StateData[] = [
    {
      id: 'ES',
      name: 'Espírito Santo',
      totalBudget: 'R$ 3,76 Bi',
      fixedBudget: 'R$ 1,72 Bi',
      variableBudget: 'R$ 2,04 Bi',
      totalExpenses: 'R$ 3,68 Bi',
      fixedExpenses: 'R$ 643,05 Mi',
      variableExpenses: 'R$ 636,70 Mi',
      disposableValue: 'R$ 1,20 Bi',
      ides: 6.4,
      idesBasicEd: 5.3,
      idesHighSchool: 4.7,
      idesAverage: 6.8
    },
    {
      id: 'MG',
      name: 'Minas Gerais',
      totalBudget: 'R$ 21,24 Bi',
      fixedBudget: 'R$ 16,20 Bi',
      variableBudget: 'R$ 6,04 Bi',
      totalExpenses: 'R$ 11,96 Bi',
      fixedExpenses: 'R$ 6,27 Bi',
      variableExpenses: 'R$ 4,20 Bi',
      disposableValue: 'R$ 3,34 Bi',
      ides: 6.2,
      idesBasicEd: 4.6,
      idesHighSchool: 4.0,
      idesAverage: 6.8
    },
    {
      id: 'RJ',
      name: 'Rio de Janeiro',
      totalBudget: 'R$ 8,61 Bi',
      fixedBudget: 'R$ 5,41 Bi',
      variableBudget: 'R$ 3,10 Bi',
      totalExpenses: 'R$ 6,40 Bi',
      fixedExpenses: 'R$ 3,75 Bi',
      variableExpenses: 'R$ 2,65 Bi',
      disposableValue: 'R$ 467,79 Mi',
      ides: 5.8,
      idesBasicEd: 3.8,
      idesHighSchool: 3.3,
      idesAverage: 6.4
    },
    {
      id: 'SP',
      name: 'São Paulo',
      totalBudget: 'R$ 72,02 Bi',
      fixedBudget: 'R$ 56,12 Bi',
      variableBudget: 'R$ 16,90 Bi',
      totalExpenses: 'R$ 32,49 Bi',
      fixedExpenses: 'R$ 25,54 Bi',
      variableExpenses: 'R$ 8,95 Bi',
      disposableValue: 'R$ 8,05 Bi',
      ides: 6.2,
      idesBasicEd: 5.1,
      idesHighSchool: 4.2,
      idesAverage: 6.9
    }
  ];

  const getIdesColor = (value: number): string => {
    if (value >= 6.0) return '#10B981'; // Verde
    if (value >= 5.0) return '#F59E0B'; // Amarelo
    if (value >= 4.0) return '#EF4444'; // Vermelho
    return '#DC2626'; // Vermelho escuro
  };

  return (
    <div style={{
      background: '#FFFFFF',
      borderRadius: '16px',
      padding: '0',
      border: '1px solid #E5E7EB',
      overflow: 'hidden'
    }}>
      {/* Table Container com scroll horizontal */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '13px'
        }}>
          {/* Header */}
          <thead>
            <tr style={{ background: '#F9FAFB' }}>
              <th style={{
                padding: '12px 16px',
                textAlign: 'left',
                fontWeight: 600,
                color: '#374151',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                borderBottom: '2px solid #E5E7EB',
                position: 'sticky',
                left: 0,
                background: '#F9FAFB',
                zIndex: 10
              }}>
                ESTADOS
              </th>
              <th style={{
                padding: '12px 16px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#374151',
                fontSize: '10px',
                borderBottom: '2px solid #E5E7EB',
                minWidth: '100px'
              }}>
                ORÇAMENTO<br/>TOTAL
              </th>
              <th style={{
                padding: '12px 16px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#374151',
                fontSize: '10px',
                borderBottom: '2px solid #E5E7EB',
                minWidth: '100px'
              }}>
                ORÇAMENTO<br/>FIXO
              </th>
              <th style={{
                padding: '12px 16px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#374151',
                fontSize: '10px',
                borderBottom: '2px solid #E5E7EB',
                minWidth: '100px'
              }}>
                ORÇAMENTO<br/>VARIÁVEL
              </th>
              <th style={{
                padding: '12px 16px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#374151',
                fontSize: '10px',
                borderBottom: '2px solid #E5E7EB',
                minWidth: '100px'
              }}>
                DESPESAS<br/>TOTAL
              </th>
              <th style={{
                padding: '12px 16px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#374151',
                fontSize: '10px',
                borderBottom: '2px solid #E5E7EB',
                minWidth: '100px'
              }}>
                DESPESAS<br/>FIXAS
              </th>
              <th style={{
                padding: '12px 16px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#374151',
                fontSize: '10px',
                borderBottom: '2px solid #E5E7EB',
                minWidth: '100px'
              }}>
                DESPESAS<br/>VARIÁVEIS
              </th>
              <th style={{
                padding: '12px 16px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#10B981',
                fontSize: '10px',
                borderBottom: '2px solid #E5E7EB',
                minWidth: '100px'
              }}>
                VALOR<br/>DISPONÍVEL
              </th>
              {/* Coluna cinza - IDES */}
              <th colSpan={5} style={{
                padding: '12px 16px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#FFFFFF',
                fontSize: '11px',
                background: '#6B7280',
                borderBottom: '2px solid #E5E7EB'
              }}>
                INDICADORES ÍDICA
              </th>
            </tr>
            {/* Sub-header para IDES */}
            <tr style={{ background: '#F3F4F6' }}>
              <th style={{ borderBottom: '1px solid #E5E7EB' }}></th>
              <th style={{ borderBottom: '1px solid #E5E7EB' }}></th>
              <th style={{ borderBottom: '1px solid #E5E7EB' }}></th>
              <th style={{ borderBottom: '1px solid #E5E7EB' }}></th>
              <th style={{ borderBottom: '1px solid #E5E7EB' }}></th>
              <th style={{ borderBottom: '1px solid #E5E7EB' }}></th>
              <th style={{ borderBottom: '1px solid #E5E7EB' }}></th>
              <th style={{ borderBottom: '1px solid #E5E7EB' }}></th>
              <th style={{
                padding: '8px 12px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#6B7280',
                fontSize: '9px',
                borderBottom: '1px solid #E5E7EB',
                background: '#F9FAFB'
              }}>
                FONTE<br/>DO<br/>RECURSO
              </th>
              <th style={{
                padding: '8px 12px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#6B7280',
                fontSize: '9px',
                borderBottom: '1px solid #E5E7EB',
                background: '#F9FAFB'
              }}>
                RECURSO<br/>DO VAAR
              </th>
              <th style={{
                padding: '8px 12px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#6B7280',
                fontSize: '9px',
                borderBottom: '1px solid #E5E7EB',
                background: '#F9FAFB'
              }}>
                IDES<br/>EDU.<br/>BÁSICA
              </th>
              <th style={{
                padding: '8px 12px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#6B7280',
                fontSize: '9px',
                borderBottom: '1px solid #E5E7EB',
                background: '#F9FAFB'
              }}>
                IDES<br/>ENSINO<br/>MÉDIO
              </th>
              <th style={{
                padding: '8px 12px',
                textAlign: 'center',
                fontWeight: 600,
                color: '#6B7280',
                fontSize: '9px',
                borderBottom: '1px solid #E5E7EB',
                background: '#F9FAFB'
              }}>
                SAEB<br/>INC
              </th>
            </tr>
          </thead>

          {/* Body */}
          <tbody>
            {states.map((state, index) => (
              <tr key={state.id} style={{
                background: index % 2 === 0 ? '#FFFFFF' : '#F9FAFB',
                transition: 'background 0.2s'
              }}>
                {/* Nome do Estado */}
                <td style={{
                  padding: '16px',
                  fontWeight: 600,
                  color: '#1F2937',
                  borderBottom: '1px solid #E5E7EB',
                  position: 'sticky',
                  left: 0,
                  background: index % 2 === 0 ? '#FFFFFF' : '#F9FAFB',
                  zIndex: 9
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{
                      width: '24px',
                      height: '24px',
                      borderRadius: '4px',
                      background: '#8B5CF6',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#FFFFFF',
                      fontSize: '10px',
                      fontWeight: 700
                    }}>
                      {state.id}
                    </div>
                    {state.name}
                  </div>
                </td>

                {/* Valores Financeiros */}
                <td style={{ padding: '16px', textAlign: 'center', color: '#374151', borderBottom: '1px solid #E5E7EB', fontWeight: 500 }}>
                  {state.totalBudget}
                </td>
                <td style={{ padding: '16px', textAlign: 'center', color: '#374151', borderBottom: '1px solid #E5E7EB', fontWeight: 500 }}>
                  {state.fixedBudget}
                </td>
                <td style={{ padding: '16px', textAlign: 'center', color: '#374151', borderBottom: '1px solid #E5E7EB', fontWeight: 500 }}>
                  {state.variableBudget}
                </td>
                <td style={{ padding: '16px', textAlign: 'center', color: '#374151', borderBottom: '1px solid #E5E7EB', fontWeight: 500 }}>
                  {state.totalExpenses}
                </td>
                <td style={{ padding: '16px', textAlign: 'center', color: '#374151', borderBottom: '1px solid #E5E7EB', fontWeight: 500 }}>
                  {state.fixedExpenses}
                </td>
                <td style={{ padding: '16px', textAlign: 'center', color: '#374151', borderBottom: '1px solid #E5E7EB', fontWeight: 500 }}>
                  {state.variableExpenses}
                </td>
                <td style={{ padding: '16px', textAlign: 'center', color: '#10B981', borderBottom: '1px solid #E5E7EB', fontWeight: 700 }}>
                  {state.disposableValue}
                </td>

                {/* Ícones de Ação */}
                <td style={{ padding: '16px', textAlign: 'center', borderBottom: '1px solid #E5E7EB' }}>
                  <button style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    border: 'none',
                    background: '#8B5CF6',
                    color: '#FFFFFF',
                    fontSize: '16px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto'
                  }}>
                    📊
                  </button>
                </td>
                <td style={{ padding: '16px', textAlign: 'center', borderBottom: '1px solid #E5E7EB' }}>
                  <button style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    border: 'none',
                    background: '#7C3AED',
                    color: '#FFFFFF',
                    fontSize: '16px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto'
                  }}>
                    🎯
                  </button>
                </td>

                {/* IDES Scores */}
                <td style={{
                  padding: '16px',
                  textAlign: 'center',
                  borderBottom: '1px solid #E5E7EB',
                  fontWeight: 700,
                  fontSize: '14px',
                  color: getIdesColor(state.ides)
                }}>
                  {state.ides}
                </td>
                <td style={{
                  padding: '16px',
                  textAlign: 'center',
                  borderBottom: '1px solid #E5E7EB',
                  fontWeight: 700,
                  fontSize: '14px',
                  color: getIdesColor(state.idesBasicEd)
                }}>
                  {state.idesBasicEd}
                </td>
                <td style={{
                  padding: '16px',
                  textAlign: 'center',
                  borderBottom: '1px solid #E5E7EB',
                  fontWeight: 700,
                  fontSize: '14px',
                  color: getIdesColor(state.idesHighSchool)
                }}>
                  {state.idesHighSchool}
                </td>
                <td style={{
                  padding: '16px',
                  textAlign: 'center',
                  borderBottom: '1px solid #E5E7EB',
                  fontWeight: 700,
                  fontSize: '14px',
                  color: getIdesColor(state.idesAverage)
                }}>
                  {state.idesAverage}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StatesTable;
