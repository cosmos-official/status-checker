async function fetchJSON(url) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return await resp.json();
}

function generateUptimeData(changes) {
  // 90일간의 실제 가용성 데이터 계산
  const days = 90;
  const data = [];
  const labels = [];
  const colors = [];
  
  // 각 날짜별 다운타임 시간을 계산
  const dailyDowntime = {};
  
  changes.forEach(change => {
    const changeDate = new Date(change.changed_at);
    const dateKey = changeDate.toISOString().split('T')[0]; // YYYY-MM-DD 형식
    
    if (!dailyDowntime[dateKey]) {
      dailyDowntime[dateKey] = { downtime: 0, totalChanges: 0 };
    }
    
    // DOWN 상태로 변경된 경우 다운타임으로 계산
    if (change.current_status === 'DOWN') {
      dailyDowntime[dateKey].downtime += 1;
    }
    dailyDowntime[dateKey].totalChanges += 1;
  });
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    const dateKey = date.toISOString().split('T')[0];
    labels.push(date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }));
    
    // 해당 날짜의 가용성 계산
    const dayData = dailyDowntime[dateKey];
    let uptime = 100; // 기본값 100%
    
    if (dayData && dayData.totalChanges > 0) {
      // 다운타임 비율 계산 (간단한 추정)
      const downtimeRatio = dayData.downtime / dayData.totalChanges;
      uptime = Math.max(0, 100 - (downtimeRatio * 20)); // 다운타임 비율에 따른 가용성 감소
    }
    
    // 모든 막대의 높이를 동일하게 (100으로 고정)
    data.push(100);
    
    // 가용성에 따른 색깔 결정
    if (uptime >= 99) {
      colors.push('#22c55e'); // 초록색 (정상)
    } else if (uptime >= 90) {
      colors.push('#f59e0b'); // 노란색 (부분 장애)
    } else {
      colors.push('#ef4444'); // 빨간색 (장애)
    }
  }
  
  return { labels, data, colors };
}

function renderUptimeChart(changes) {
  const ctx = document.getElementById('uptime-chart');
  if (!ctx) return;
  
  const { labels, data, colors } = generateUptimeData(changes);
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: '가용성 (%)',
        data: data,
        backgroundColor: colors,
        borderColor: colors,
        borderWidth: 0,
        borderRadius: 2,
        barThickness: 6,
        maxBarThickness: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: true,
          callbacks: {
            title: function(context) {
              return context[0].label;
            },
            label: function() {
              return null;
            }
          }
        }
      },
      scales: {
        x: {
          display: false
        },
        y: {
          display: false,
          min: 0,
          max: 100
        }
      }
    }
  });
}

function renderStatusTable(statusData) {
  const tbody = document.querySelector('#status-table tbody');
  tbody.innerHTML = '';
  Object.values(statusData).forEach(server => {
    const tr = document.createElement('tr');
    const localTime = server.checked_at ? new Date(server.checked_at).toLocaleString('ko-KR') : '-';
    tr.innerHTML = `
      <td>${server.server_id}</td>
      <td class="status-${server.status.toLowerCase()}">${server.status}</td>
      <td>${server.response_time ?? '-'}</td>
      <td>${localTime}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderChangesTable(changes) {
  const tbody = document.querySelector('#changes-table tbody');
  tbody.innerHTML = '';
  changes.slice(-20).reverse().forEach(change => {
    const tr = document.createElement('tr');
    const localTime = new Date(change.changed_at).toLocaleString('ko-KR');
    tr.innerHTML = `
      <td>${change.server_name}</td>
      <td>${change.previous_status}</td>
      <td>${change.current_status}</td>
      <td>${localTime}</td>
      <td>${change.error_message ?? ''}</td>
    `;
    tbody.appendChild(tr);
  });
}

async function main() {
  try {
    const [status, changes] = await Promise.all([
      fetchJSON('../data/current-status.json'),
      fetchJSON('../data/status-changes.json')
    ]);
    
    renderUptimeChart(changes.changes || []);
    renderStatusTable(status);
    renderChangesTable(changes.changes || []);
  } catch (e) {
    document.body.innerHTML = `<p style='color:red'>데이터 로드 실패: ${e}</p>`;
  }
}

main(); 