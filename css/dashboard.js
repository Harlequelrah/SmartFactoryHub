// Données pour les graphiques en Barres (Graph 1 et Graph 2)
const dataBar1 = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
        label: 'Échantillons soumis',
        data: [12, 19, 3, 5, 2, 3],
        backgroundColor: '#FF5733',
        borderColor: '#FF5733',
        borderWidth: 1
    }]
};

const dataBar2 = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
        label: 'Échantillons testés',
        data: [10, 18, 5, 7, 4, 6],
        backgroundColor: '#33C3FF',
        borderColor: '#33C3FF',
        borderWidth: 1
    }]
};

// Données pour le graphique en Diagramme de Secteurs
const dataPie = {
    labels: ['A', 'B', 'C', 'D'],
    datasets: [{
        data: [300, 50, 100, 150],
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
        hoverBackgroundColor: ['#FF4384', '#36A2FB', '#FFDE56', '#4BC0D0']
    }]
};

// Création du graphique en Barres (Graph 1)
const ctx1 = document.getElementById('myChart1').getContext('2d');
const myChart1 = new Chart(ctx1, {
    type: 'bar',
    data: dataBar1,
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Création du graphique en Barres (Graph 2)
const ctx2 = document.getElementById('myChart2').getContext('2d');
const myChart2 = new Chart(ctx2, {
    type: 'bar',
    data: dataBar2,
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Création du graphique en Diagramme de Secteurs
const ctx3 = document.getElementById('myChart3').getContext('2d');
const myChart3 = new Chart(ctx3, {
    type: 'pie',
    data: dataPie,
    options: {
        responsive: true
    }
});
