// Dashboard Enterprise JavaScript - GitHub Style

// Chart.js default configuration
Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#57606a';

// Global chart instances
let adminCharts = {};

// Admin Dashboard Functions
function loadAdminCharts() {
    console.log('Loading admin charts...');

    const chartsToLoad = ['planChart', 'statusChart'];
    if (document.getElementById('payoutStatusChart')) {
        chartsToLoad.push('payoutStatusChart');
    }

    chartsToLoad.forEach(markChartLoading);

    fetch('/dashboard/api/admin-stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Charts data received:', data);
            removeLoadingStates(chartsToLoad);
            createPlanDistributionChart(data.plan_distribution);
            createStatusDistributionChart(data.status_distribution);
            if (data.payout_distribution && chartsToLoad.includes('payoutStatusChart')) {
                createPayoutStatusChart(data.payout_distribution);
            } else if (chartsToLoad.includes('payoutStatusChart')) {
                showChartError(['payoutStatusChart']);
            }
        })
        .catch(error => {
            console.error('Error loading admin charts:', error);
            showChartError(chartsToLoad);
        });

    // Load admin clicks chart
    loadAdminClicksChart();
}

function loadAdminClicksChart() {
    const ctx = document.getElementById('adminClicksChart');
    if (!ctx) {
        console.log('adminClicksChart canvas not found');
        return;
    }
    
    console.log('Loading admin clicks chart...');

    markChartLoading('adminClicksChart');
    
    fetch('/dashboard/api/admin-clicks')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load admin clicks data');
            }
            return response.json();
        })
        .then(data => {
            console.log('Admin clicks data received:', data);
            
            if (adminCharts.adminClicksChart) {
                adminCharts.adminClicksChart.destroy();
            }
            
            adminCharts.adminClicksChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#24292f',
                            padding: 12,
                            borderColor: '#d0d7de',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                color: '#57606a'
                            },
                            grid: {
                                color: '#d0d7de'
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 0,
                                color: '#57606a'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .then(() => {
            markChartLoaded('adminClicksChart');
        })
        .catch(error => {
            console.error('Error loading admin clicks chart:', error);
            showChartError(['adminClicksChart']);
        });
}

function markChartLoaded(chartId) {
    const canvas = document.getElementById(chartId);
    if (!canvas) {
        return;
    }

    const container = canvas.parentElement;
    if (!container) {
        return;
    }

    container.classList.remove('chart-loading');
    container.classList.add('chart-loaded');
    container.setAttribute('aria-busy', 'false');

    const skeleton = container.querySelector('.chart-skeleton');
    if (skeleton) {
        skeleton.remove();
    }

    const errorBanner = container.querySelector('.chart-error');
    if (errorBanner) {
        errorBanner.remove();
    }

    canvas.hidden = false;
    canvas.style.opacity = 1;
    canvas.removeAttribute('aria-hidden');
}

function markChartLoading(chartId) {
    const canvas = document.getElementById(chartId);
    if (!canvas) {
        return;
    }

    const container = canvas.parentElement;
    if (!container) {
        return;
    }

    container.classList.add('chart-loading');
    container.classList.remove('chart-loaded');
    container.setAttribute('aria-busy', 'true');

    const errorBanner = container.querySelector('.chart-error');
    if (errorBanner) {
        errorBanner.remove();
    }

    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.opacity = 0;

    if (!container.querySelector('.chart-skeleton')) {
        const skeleton = document.createElement('div');
        skeleton.className = 'chart-skeleton';
        skeleton.setAttribute('aria-hidden', 'true');
        container.insertBefore(skeleton, canvas);
    }
}

function removeLoadingStates(chartIds = []) {
    const targets = chartIds.length ? chartIds : ['planChart', 'statusChart'];
    targets.forEach(markChartLoaded);
}

function createPlanDistributionChart(data) {
    const ctx = document.getElementById('planChart');
    if (!ctx) {
        console.error('planChart canvas not found');
        return;
    }
    
    if (adminCharts.planChart) {
        adminCharts.planChart.destroy();
    }
    
    console.log('Creating plan distribution chart');
    
    adminCharts.planChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        color: '#24292f',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#24292f',
                    padding: 12,
                    borderColor: '#d0d7de',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function createStatusDistributionChart(data) {
    const ctx = document.getElementById('statusChart');
    if (!ctx) {
        console.error('statusChart canvas not found');
        return;
    }
    
    if (adminCharts.statusChart) {
        adminCharts.statusChart.destroy();
    }
    
    console.log('Creating status distribution chart');
    
    adminCharts.statusChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#24292f',
                    padding: 12,
                    borderColor: '#d0d7de',
                    borderWidth: 1,
                    callbacks: {
                        title: function(context) {
                            return `Status: ${context[0].label}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        color: '#57606a'
                    },
                    grid: {
                        color: '#d0d7de'
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 0,
                        color: '#57606a'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createPayoutStatusChart(data) {
    const ctx = document.getElementById('payoutStatusChart');
    if (!ctx) {
        console.error('payoutStatusChart canvas not found');
        return;
    }

    if (adminCharts.payoutStatusChart) {
        adminCharts.payoutStatusChart.destroy();
    }

    if (!data || !Array.isArray(data.labels) || !Array.isArray(data.datasets)) {
        console.error('Invalid payout distribution data');
        showChartError(['payoutStatusChart']);
        return;
    }

    adminCharts.payoutStatusChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true,
                        color: '#24292f'
                    }
                },
                tooltip: {
                    backgroundColor: '#24292f',
                    padding: 12,
                    borderColor: '#d0d7de',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const value = context.parsed;
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Error handling
function showChartError(chartIds) {
    chartIds.forEach(id => {
        const canvas = document.getElementById(id);
        const container = canvas?.parentElement;
        if (!container) {
            return;
        }

        container.classList.remove('chart-loading', 'chart-loaded');
        container.setAttribute('aria-busy', 'false');

        const skeleton = container.querySelector('.chart-skeleton');
        if (skeleton) {
            skeleton.remove();
        }

        let errorBanner = container.querySelector('.chart-error');
        if (!errorBanner) {
            errorBanner = document.createElement('div');
            errorBanner.className = 'chart-error';
            errorBanner.setAttribute('role', 'status');
            errorBanner.setAttribute('aria-live', 'assertive');
            errorBanner.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Erro ao carregar gráfico';
            container.appendChild(errorBanner);
        }

        if (canvas) {
            canvas.setAttribute('aria-hidden', 'true');
            canvas.style.opacity = 0;
        }
    });
}

function initSortableTables() {
    const tables = document.querySelectorAll('[data-sortable-table]');

    tables.forEach((table, index) => {
        const tbody = table.tBodies[0];
        if (!tbody) {
            return;
        }

        if (!table.dataset.tableId) {
            table.dataset.tableId = `sortable-${index}`;
        }

        const cardsContainer = findCardsContainer(table);
        const cards = cardsContainer ? Array.from(cardsContainer.children) : [];
        const rows = Array.from(tbody.rows);

        rows.forEach((row, rowIndex) => {
            const key = `${table.dataset.tableId}-${rowIndex}`;
            row.dataset.tableSortKey = key;
            if (cards[rowIndex]) {
                cards[rowIndex].dataset.tableSortKey = key;
            }
        });

        const headerButtons = table.querySelectorAll('.table-sort');
        headerButtons.forEach(button => {
            button.setAttribute('aria-pressed', 'false');
            const th = button.closest('th');
            if (th) {
                th.setAttribute('aria-sort', 'none');
            }
            button.addEventListener('click', () => handleSortButton(table, button, cardsContainer));
        });
    });
}

function findCardsContainer(table) {
    const wrapper = table.closest('[data-table-wrapper]');
    if (!wrapper) {
        return null;
    }

    if (wrapper.nextElementSibling && wrapper.nextElementSibling.hasAttribute('data-table-cards')) {
        return wrapper.nextElementSibling;
    }

    if (wrapper.parentElement) {
        return wrapper.parentElement.querySelector('[data-table-cards]');
    }

    return null;
}

function handleSortButton(table, button, cardsContainer) {
    const columnIndex = parseInt(button.dataset.columnIndex || '0', 10);
    const sortType = button.dataset.sortType || 'text';
    const currentDirection = button.dataset.sortDirection === 'asc' ? 'desc' : 'asc';

    updateSortIndicators(table, button, currentDirection);

    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);

    rows.sort((a, b) => compareRows(a, b, columnIndex, sortType, currentDirection));

    const fragment = document.createDocumentFragment();
    rows.forEach(row => fragment.appendChild(row));
    tbody.appendChild(fragment);

    if (cardsContainer) {
        reorderTableCards(cardsContainer, rows);
    }
}

function compareRows(rowA, rowB, columnIndex, sortType, direction) {
    const cellA = rowA.cells[columnIndex];
    const cellB = rowB.cells[columnIndex];

    const valueA = getCellSortValue(cellA, sortType);
    const valueB = getCellSortValue(cellB, sortType);

    if (valueA === valueB) {
        return 0;
    }

    const multiplier = direction === 'asc' ? 1 : -1;
    return valueA > valueB ? 1 * multiplier : -1 * multiplier;
}

function getCellSortValue(cell, sortType) {
    if (!cell) {
        return '';
    }

    const dataValue = cell.getAttribute('data-sort-value');

    if (sortType === 'number') {
        const raw = dataValue ?? cell.textContent;
        const numeric = parseFloat(String(raw).replace(/[^0-9.-]/g, ''));
        return Number.isNaN(numeric) ? 0 : numeric;
    }

    const text = dataValue ?? cell.textContent;
    return String(text).trim().toLowerCase();
}

function updateSortIndicators(table, activeButton, direction) {
    const allButtons = table.querySelectorAll('.table-sort');
    allButtons.forEach(button => {
        button.dataset.sortDirection = '';
        button.classList.remove('is-active');
        button.setAttribute('aria-pressed', 'false');
        const icon = button.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-sort-up', 'fa-sort-down');
            if (!icon.classList.contains('fa-sort')) {
                icon.classList.add('fa-sort');
            }
        }
        const th = button.closest('th');
        if (th) {
            th.setAttribute('aria-sort', 'none');
        }
    });

    activeButton.dataset.sortDirection = direction;
    activeButton.classList.add('is-active');
    activeButton.setAttribute('aria-pressed', 'true');

    const icon = activeButton.querySelector('i');
    if (icon) {
        icon.classList.remove('fa-sort');
        icon.classList.add(direction === 'asc' ? 'fa-sort-up' : 'fa-sort-down');
    }

    const th = activeButton.closest('th');
    if (th) {
        th.setAttribute('aria-sort', direction === 'asc' ? 'ascending' : 'descending');
    }
}

function reorderTableCards(cardsContainer, sortedRows) {
    if (!cardsContainer) {
        return;
    }

    const cardMap = new Map();
    Array.from(cardsContainer.children).forEach(card => {
        cardMap.set(card.dataset.tableSortKey, card);
    });

    const fragment = document.createDocumentFragment();
    sortedRows.forEach(row => {
        const key = row.dataset.tableSortKey;
        const card = key ? cardMap.get(key) : null;
        if (card) {
            fragment.appendChild(card);
        }
    });

    cardsContainer.appendChild(fragment);
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, checking for charts...');
    
    // Check if we're on admin dashboard
    const planChart = document.getElementById('planChart');
    const statusChart = document.getElementById('statusChart');
    
    // Check if we're on client dashboard
    const clicksChart = document.getElementById('clicksChart');
    const domainChart = document.getElementById('domainChart');

    initSortableTables();
    
    if (planChart && statusChart) {
        console.log('Admin dashboard detected, loading charts...');
        loadAdminCharts();
    } else if (clicksChart || domainChart) {
        console.log('Client dashboard detected, loading charts...');
        loadClientCharts();
    } else {
        console.log('No charts detected on this page');
    }
});

// Client Dashboard Functions
let clientCharts = {};
let currentClicksPeriod = 30;

function loadClientCharts() {
    console.log('Loading client charts...');
    loadClicksChart(currentClicksPeriod);
    loadDomainChart();
}

function loadClicksChart(days = 30) {
    const ctx = document.getElementById('clicksChart');
    if (!ctx) {
        console.error('clicksChart canvas not found');
        return;
    }
    
    console.log(`Loading clicks chart for ${days} days...`);
    
    fetch(`/dashboard/api/clicks-chart?days=${days}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load clicks data');
            }
            return response.json();
        })
        .then(data => {
            console.log('Clicks data received:', data);
            
            if (clientCharts.clicksChart) {
                clientCharts.clicksChart.destroy();
            }
            
            clientCharts.clicksChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#24292f',
                            padding: 12,
                            borderColor: '#d0d7de',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                color: '#57606a'
                            },
                            grid: {
                                color: '#d0d7de'
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 0,
                                color: '#57606a'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading clicks chart:', error);
            showChartError(['clicksChart']);
        });
}

function loadDomainChart() {
    const ctx = document.getElementById('domainChart');
    if (!ctx) {
        console.error('domainChart canvas not found');
        return;
    }
    
    console.log('Loading domain chart...');
    
    fetch('/dashboard/api/domain-stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load domain stats');
            }
            return response.json();
        })
        .then(data => {
            console.log('Domain stats received:', data);
            
            if (clientCharts.domainChart) {
                clientCharts.domainChart.destroy();
            }
            
            clientCharts.domainChart = new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#24292f',
                            padding: 12,
                            borderColor: '#d0d7de',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                color: '#57606a'
                            },
                            grid: {
                                color: '#d0d7de'
                            }
                        },
                        y: {
                            ticks: {
                                color: '#57606a'
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading domain chart:', error);
            showChartError(['domainChart']);
        });
}

function changeClicksPeriod(days, button) {
    currentClicksPeriod = days;
    
    // Update button states
    const buttons = button.parentElement.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    button.classList.remove('btn-outline-primary');
    button.classList.add('btn-primary');
    
    // Reload chart
    loadClicksChart(days);
}

// Export for global access
window.DashboardJS = {
    loadAdminCharts,
    loadClientCharts,
    changeClicksPeriod
};
