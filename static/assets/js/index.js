if ($('#chart1').length) {
    $(function () {
        "use strict";

        // chart 1


        fetch('/sales/graphic_user/')
            .then(response => response.json())
            .then(data => {
                var ctx = document.getElementById('chart1').getContext('2d');
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.label,
                        datasets: [{
                            label: 'Mes',
                            data: data.month,
                            backgroundColor: '#f64141',
                            borderColor: "transparent",
                            pointRadius: "0",
                            borderWidth: 3
                        }, {
                            label: 'dia',
                            data: data.sales,
                            backgroundColor: "rgba(199,226,246,0.7)",
                            borderColor: "transparent",
                            pointRadius: "0",
                            borderWidth: 5
                        }]
                    },
                    options: {
                        maintainAspectRatio: false,
                        legend: {
                            display: false,
                            labels: {
                                fontColor: '#ddd',
                                boxWidth: 40
                            }
                        },
                        tooltips: {
                            displayColors: true,
                        },
                        scales: {
                            xAxes: [{
                                ticks: {
                                    beginAtZero: true,
                                    fontColor: '#ddd'
                                },
                                gridLines: {
                                    display: true,
                                    color: "rgba(221, 221, 221, 0.08)"
                                },
                            }],
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true, //inicia desde cero
                                    fontColor: '#ddd',
                                    callback: function (value, index, ticks) {
                                        return 'S/. ' + value;
                                    }
                                },
                                gridLines: {
                                    display: true,
                                    color: "rgba(221, 221, 221, 0.08)"
                                },
                            }]
                        }

                    }
                });
            });
        // chart 2
        fetch('/sales/graphic_sales/')
            .then(response => response.json())
            .then(data => {
                var ctx = document.getElementById("chart2").getContext('2d');
                var myChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: data.label,
                        datasets: [{
                            backgroundColor: [
                                // "#ffffff",
                                "rgba(255,255,255,0.7)",
                                "rgba(255, 255, 255, 0.50)",
                                "rgba(255, 255, 255, 0.20)"
                            ],
                            data: data.total,
                            borderWidth: [0, 0, 0]
                        }]
                    },
                    options: {
                        maintainAspectRatio: false,
                        legend: {
                            position: "top",
                            display: true,
                            labels: {
                                fontColor: '#ddd',
                                boxWidth: 15
                            }
                        }
                        ,
                        tooltips: {
                            displayColors: false
                        }
                    }
                });
            });


        fetch('/sales/graphic_month/')
            .then(response => response.json())
            .then(data => {
                var ctx = document.getElementById('chart3').getContext('2d');
                var myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.label,
                        datasets: [{
                            label: '',
                            data: [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                            backgroundColor: '#fff',
                            borderColor: "transparent",
                            pointRadius: "0",
                            borderWidth: 3,
                        }, {
                            label: 'Venta',
                            data: data.d,
                            backgroundColor: "rgba(190,215,233,0.7)",
                            borderColor: "transparent",
                            pointRadius: "0",
                            borderWidth: 1,
                            // datalabels: {
                            //     color: '#f80909',
                            //     font: {
                            //         weight: 'bold',
                            //     },
                            //     formatter: (value, context) => {
                            //         return '$ ' + parseInt(5).toLocaleString('en-US');
                            //     },
                            //     //Aqui controlo la ubicacion de mis labels encima del grafico
                            //     anchor: 'end',
                            //     align: 'top',
                            //     offset: 0,
                            //     display: true
                            // }
                        },

                        ]
                    },
                    options: {
                        maintainAspectRatio: false,
                        legend: {
                            display: false,
                            labels: {
                                fontColor: '#ddd',
                                boxWidth: 40
                            }
                        },
                        tooltips: {
                            displayColors: false
                        },
                        scales: {
                            xAxes: [{
                                ticks: {
                                    beginAtZero: true,
                                    fontColor: '#ddd'
                                },
                                gridLines: {
                                    display: true,
                                    color: "rgba(221, 221, 221, 0.08)"
                                },
                            }],
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true,
                                    fontColor: '#ddd',
                                    callback: function (value, index, ticks) {
                                        return 'S/. ' + value;
                                    }
                                },
                                gridLines: {
                                    display: true,
                                    color: "rgba(221, 221, 221, 0.08)"
                                },
                            }]
                        }

                    }
                });


            });

    });
}

var firebaseConfig = {
    apiKey: "AIzaSyCcsLgiNVizdQWF8WRTkzxEycpoaxOLTaQ",
    authDomain: "deliveryapp-e121f.firebaseapp.com",
    databaseURL: "https://deliveryapp-e121f-default-rtdb.firebaseio.com",
    projectId: "deliveryapp-e121f",
    storageBucket: "deliveryapp-e121f.appspot.com",
    messagingSenderId: "1057170340379",
    appId: "1:1057170340379:web:695b4a3edf0297215616be",
    measurementId: "G-VYS4J0M1LE"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
firebase.analytics();
