// Dashboard Enterprise JavaScript Functions

// Chart.js default configuration
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#6c757d';

// Global chart instances
let adminCharts = {};
let clientCharts = {};

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR');
}

// Admin Dashboard Functions
function loadAdminCharts() {
    showChartLoading(['planChart', 'statusChart']);
    
    fetch('/dashboard/api/admin-stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            createPlanDistributionChart(data.plan_distribution);
            createStatusDistributionChart(data.status_distribution);
        })
        .catch(error => {
            console.error('Error loading admin charts:', error);
            showChartError(['planChart', 'statusChart']);
        });
}

function createPlanDistributionChart(data) {
    const ctx = document.getElementById('planChart');
    if (!ctx) return;
    
    if (adminCharts.planChart) {
        adminCharts.planChart.destroy();
    }
    
    adminCharts.planChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
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
    if (!ctx) return;
    
    if (adminCharts.statusChart) {
        adminCharts.statusChart.destroy();
    }
    
    adminCharts.statusChart = new Chart(ctx.getContext('2d'), {
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
                        stepSize: 1
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 0
                    }
                }
            }
        }
    });
}

// Client Dashboard Functions
function loadClientCharts(days = 30) {
    loadClicksChart(days);
    loadDomainChart();
}

function loadClicksChart(days = 30) {
    showChartLoading(['clicksChart']);
    
    fetch(`/dashboard/api/clicks-chart?days=${days}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            createClicksChart(data);
        })
        .catch(error => {
            console.error('Error loading clicks chart:', error);
            showChartError(['clicksChart']);
        });
}

function createClicksChart(data) {
    const ctx = document.getElementById('clicksChart');
    if (!ctx) return;
    
    if (clientCharts.clicksChart) {
        clientCharts.clicksChart.destroy();
    }
    
    clientCharts.clicksChart = new Chart(ctx.getContext('2d'), {
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
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        title: function(context) {
                            return `Data: ${context[0].label}`;
                        },
                        label: function(context) {
                            return `Clicks: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6
                },
                line: {
                    tension: 0.3
                }
            }
        }
    });
}

function loadDomainChart() {
    showChartLoading(['domainChart']);
    
    fetch('/dashboard/api/domain-stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            createDomainChart(data);
        })
        .catch(error => {
            console.error('Error loading domain chart:', error);
            showChartError(['domainChart']);
        });
}

function createDomainChart(data) {
    const ctx = document.getElementById('domainChart');
    if (!ctx) return;
    
    if (clientCharts.domainChart) {
        clientCharts.domainChart.destroy();
    }
    
    clientCharts.domainChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    return {
                                        text: `${label}: ${value}`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        strokeStyle: data.datasets[0].backgroundColor[i],
                                        pointStyle: 'circle'
                                    };
                                });
                            }
                            return [];
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} clicks (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Utility functions for chart management
function showChartLoading(chartIds) {
    chartIds.forEach(id => {
        const container = document.getElementById(id)?.parentElement;
        if (container) {
            container.classList.add('chart-loading');
        }
    });
}

function showChartError(chartIds) {
    chartIds.forEach(id => {
        const container = document.getElementById(id)?.parentElement;
        if (container) {
            container.classList.remove('chart-loading');
            container.innerHTML = '<div class="text-center text-muted py-5">Erro ao carregar gráfico</div>';
        }
    });
}

// Period change function for clicks chart
function changeClicksPeriod(days, buttonElement) {
    // Update button states
    const buttons = buttonElement.parentElement.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    buttonElement.classList.remove('btn-outline-primary');
    buttonElement.classList.add('btn-primary');
    
    // Reload chart
    loadClicksChart(days);
}

// Auto-refresh functionality
function startAutoRefresh(interval = 300000) { // 5 minutes
    setInterval(() => {
        if (document.getElementById('planChart')) {
            loadAdminCharts();
        }
        if (document.getElementById('clicksChart')) {
            loadClientCharts();
        }
    }, interval);
}

// Initialize dashboard based on page type
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on admin dashboard
    if (document.getElementById('planChart')) {
        loadAdminCharts();
    }
    
    // Check if we're on client dashboard
    if (document.getElementById('clicksChart')) {
        loadClientCharts(30);
    }
    
    // Start auto-refresh (optional)
    // startAutoRefresh();
});

// Export functions for global access
window.DashboardJS = {
    loadAdminCharts,
    loadClientCharts,
    changeClicksPeriod,
    formatNumber,
    formatCurrency,
    formatDate
};