// Algoritmo K-means para clustering de comportamentos orçamentários

export interface ClusterPoint {
  year: number;
  value: number;
  deviation: number; // Desvio da média
  isElectionYear: boolean;
  executionRate: number;
}

export interface Cluster {
  id: number;
  name: string;
  description: string;
  color: string;
  points: ClusterPoint[];
  centroid: { deviation: number; executionRate: number };
}

// Calcula distância euclidiana entre dois pontos
const euclideanDistance = (
  p1: { deviation: number; executionRate: number },
  p2: { deviation: number; executionRate: number }
): number => {
  return Math.sqrt(
    Math.pow(p1.deviation - p2.deviation, 2) +
    Math.pow(p1.executionRate - p2.executionRate, 2)
  );
};

// Algoritmo K-means
export const kMeansClustering = (
  points: ClusterPoint[],
  k: number = 4,
  maxIterations: number = 100
): Cluster[] => {
  // Normaliza os dados (0-1) para melhor clustering
  const deviations = points.map(p => p.deviation);
  const executionRates = points.map(p => p.executionRate);

  const minDev = Math.min(...deviations);
  const maxDev = Math.max(...deviations);
  const minExec = Math.min(...executionRates);
  const maxExec = Math.max(...executionRates);

  const normalizedPoints = points.map(p => ({
    ...p,
    normDeviation: (p.deviation - minDev) / (maxDev - minDev || 1),
    normExecutionRate: (p.executionRate - minExec) / (maxExec - minExec || 1)
  }));

  // Inicializa centroides (k-means++)
  const centroids: Array<{ deviation: number; executionRate: number }> = [];

  // Primeiro centroide aleatório
  const firstPoint = normalizedPoints[Math.floor(Math.random() * normalizedPoints.length)];
  centroids.push({
    deviation: firstPoint.normDeviation,
    executionRate: firstPoint.normExecutionRate
  });

  // Próximos centroides: escolhe pontos mais distantes
  for (let i = 1; i < k; i++) {
    const distances = normalizedPoints.map(p => {
      const minDist = Math.min(...centroids.map(c =>
        euclideanDistance(
          { deviation: p.normDeviation, executionRate: p.normExecutionRate },
          c
        )
      ));
      return minDist;
    });

    const maxDistIndex = distances.indexOf(Math.max(...distances));
    centroids.push({
      deviation: normalizedPoints[maxDistIndex].normDeviation,
      executionRate: normalizedPoints[maxDistIndex].normExecutionRate
    });
  }

  // Iterações K-means
  let assignments = new Array(points.length).fill(0);

  for (let iter = 0; iter < maxIterations; iter++) {
    // Atribui pontos aos clusters mais próximos
    const newAssignments = normalizedPoints.map(p => {
      const distances = centroids.map(c =>
        euclideanDistance(
          { deviation: p.normDeviation, executionRate: p.normExecutionRate },
          c
        )
      );
      return distances.indexOf(Math.min(...distances));
    });

    // Verifica convergência
    if (JSON.stringify(assignments) === JSON.stringify(newAssignments)) {
      break;
    }
    assignments = newAssignments;

    // Recalcula centroides
    for (let i = 0; i < k; i++) {
      const clusterPoints = normalizedPoints.filter((_, idx) => assignments[idx] === i);
      if (clusterPoints.length > 0) {
        centroids[i] = {
          deviation: clusterPoints.reduce((sum, p) => sum + p.normDeviation, 0) / clusterPoints.length,
          executionRate: clusterPoints.reduce((sum, p) => sum + p.normExecutionRate, 0) / clusterPoints.length
        };
      }
    }
  }

  // Nomeia e caracteriza clusters baseado nos centroides
  const clusterInfos = centroids.map((centroid, idx) => {
    const avgDeviation = centroid.deviation * (maxDev - minDev) + minDev;
    const avgExecution = centroid.executionRate * (maxExec - minExec) + minExec;

    let name = '';
    let description = '';
    let color = '';

    if (avgDeviation > 10 && avgExecution > 80) {
      name = 'Expansão com Alta Execução';
      description = 'Anos com aumento orçamentário e execução eficiente';
      color = '#10b981'; // Verde
    } else if (avgDeviation > 10 && avgExecution <= 80) {
      name = 'Expansão com Subexecução';
      description = 'Anos eleitorais com aumento de verba mas execução baixa';
      color = '#f59e0b'; // Amarelo
    } else if (avgDeviation < -10) {
      name = 'Crise/Corte';
      description = 'Períodos de redução orçamentária significativa';
      color = '#ef4444'; // Vermelho
    } else {
      name = 'Comportamento Normal';
      description = 'Execução dentro da normalidade estatística';
      color = '#3b82f6'; // Azul
    }

    return { name, description, color };
  });

  // Cria clusters finais
  return centroids.map((centroid, idx) => {
    const clusterPoints = points.filter((_, pointIdx) => assignments[pointIdx] === idx);

    return {
      id: idx,
      name: clusterInfos[idx].name,
      description: clusterInfos[idx].description,
      color: clusterInfos[idx].color,
      points: clusterPoints,
      centroid: {
        deviation: centroid.deviation * (maxDev - minDev) + minDev,
        executionRate: centroid.executionRate * (maxExec - minExec) + minExec
      }
    };
  });
};

// Identifica padrões de comportamento
export const identifyBehaviorPatterns = (clusters: Cluster[]): string[] => {
  const patterns: string[] = [];

  // Padrão eleitoral
  const electoralClusters = clusters.filter(c =>
    c.points.filter(p => p.isElectionYear).length > c.points.length * 0.6
  );
  if (electoralClusters.length > 0) {
    const avgDeviation = electoralClusters[0].centroid.deviation;
    if (avgDeviation > 5) {
      patterns.push(`Anos eleitorais tendem a ter aumento de ${avgDeviation.toFixed(1)}% no orçamento`);
    }
  }

  // Padrão de crise
  const crisisClusters = clusters.filter(c => c.centroid.deviation < -15);
  if (crisisClusters.length > 0) {
    patterns.push(`Identificados ${crisisClusters[0].points.length} anos com cortes severos (>15%)`);
  }

  // Padrão de subexecução
  const subexecutionClusters = clusters.filter(c => c.centroid.executionRate < 70);
  if (subexecutionClusters.length > 0) {
    patterns.push(`${subexecutionClusters[0].points.length} anos com subexecução crítica (<70%)`);
  }

  return patterns;
};
