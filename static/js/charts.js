$(document).ready(function() {
    // Selector Chart
    $.ajax({
                url         : "/api/selectors",
                type        : "POST",
                contentType : "application/json",
                dataType    : "json",
    }).done(function (data) {
        var ctx6 = document.getElementById("dkimPolarChart").getContext('2d');
    	var doughnutChart = new Chart(ctx6, {
    		type: 'polarArea',
    		data: {
    			labels: data.labels,
    			datasets: [{
    				label: "DKIM Selector Records",
    				data: data.count,
    				backgroundColor: ["rgb(255, 99, 132)","rgb(75, 192, 192)","rgb(255, 205, 86)","rgb(201, 203, 207)","rgb(54, 162, 235)"]
    				}]
    		}
        });
    });
    
    // SELECTOR DEFAULT
    /* 
        data: {
    			labels: ["Red","Green","Yellow","Grey","Blue"],
    			datasets: [{
    				label: "My First Dataset",
    				data: [11,16,7,3,14],
    				backgroundColor: ["rgb(255, 99, 132)","rgb(75, 192, 192)","rgb(255, 205, 86)","rgb(201, 203, 207)","rgb(54, 162, 235)"]
    				}]
    		}
    		*/

    // Bar Chart
    /*
    var ctx1 = document.getElementById("barChart").getContext('2d');
	var barChart = new Chart(ctx1, {
		type: 'bar',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
			datasets: [{
				label: 'Amount received',
				data: [12, 19, 3, 5, 10, 5, 13, 17, 11, 8, 11, 9],
				backgroundColor: [
					'rgba(255, 99, 132, 0.2)',
					'rgba(54, 162, 235, 0.2)',
					'rgba(255, 206, 86, 0.2)',
					'rgba(75, 192, 192, 0.2)',
					'rgba(153, 102, 255, 0.2)',
					'rgba(255, 159, 64, 0.2)',
					'rgba(255, 99, 132, 0.2)',
					'rgba(54, 162, 235, 0.2)',
					'rgba(255, 206, 86, 0.2)',
					'rgba(75, 192, 192, 0.2)',
					'rgba(153, 102, 255, 0.2)',
					'rgba(255, 159, 64, 0.2)'				
				],
				borderColor: [
					'rgba(255,99,132,1)',
					'rgba(54, 162, 235, 1)',
					'rgba(255, 206, 86, 1)',
					'rgba(75, 192, 192, 1)',
					'rgba(153, 102, 255, 1)',
					'rgba(255, 159, 64, 1)',
					'rgba(255,99,132,1)',
					'rgba(54, 162, 235, 1)',
					'rgba(255, 206, 86, 1)',
					'rgba(75, 192, 192, 1)',
					'rgba(153, 102, 255, 1)',
					'rgba(255, 159, 64, 1)'
				],
				borderWidth: 1
			}]
		},
		options: {
			scales: {
				yAxes: [{
					ticks: {
						beginAtZero:true
					}
				}]
			}
		}
	});*/
	
	Chart.pluginService.register({
    	beforeDraw: function (chart, easing) {
    		if (chart.config.options.chartArea && chart.config.options.chartArea.backgroundColor) {
    			var helpers = Chart.helpers;
    			var ctx = chart.chart.ctx;
    			var chartArea = chart.chartArea;
    			
    			var sect = (chartArea.right - chartArea.left) / 4;
    			var rd2 = chartArea.left + sect;
    			var rd3 = rd2 + sect;
    			var rd4 = rd3 + sect;
    			    
    			ctx.save();
    			ctx.fillStyle = chart.config.options.chartArea.backgroundColor[0];
    			ctx.fillRect(chartArea.left, chartArea.top, sect, chartArea.bottom - chartArea.top);
    			ctx.fillStyle = chart.config.options.chartArea.backgroundColor[1];
    			ctx.fillRect(rd2, chartArea.top, sect, chartArea.bottom - chartArea.top);
                ctx.fillStyle = chart.config.options.chartArea.backgroundColor[0];
    			ctx.fillRect(rd3, chartArea.top, sect, chartArea.bottom - chartArea.top);
    			ctx.fillStyle = chart.config.options.chartArea.backgroundColor[1];
    			ctx.fillRect(rd4, chartArea.top, sect, chartArea.bottom - chartArea.top);
    			ctx.restore();
    		}
    	}
    });
	
	// Arrow Averages
	var ctxaca = document.getElementById("comboArrowChart").getContext('2d');
	var comboBarLineChart = new Chart(ctxaca, {
		type: 'bar',
		data: {
			labels: ["Combined", "First Arrow", "Second Arrow", "Third Arrow"],
			datasets: [{
					type: 'bar',
					label: "Average Score",
					backgroundColor: 'rgba(149,149,133, .75)',
					data: [7.91, 8.875, 8.175, 6.675]
				}], 
				borderWidth: 1
		},
		options: {
			scales: {
				yAxes: [{
					ticks: {
						beginAtZero:true
					}
				}]
			}
		}
	});
	
	var ctx1 = document.getElementById("barChart").getContext('2d');
	var barChart = new Chart(ctx1, {
		type: 'bar',
		data: {
			labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40'],
			datasets: [{
    			type: "line",
				label: 'End Score',
				data: [28, 26, 27, 28, 26, 27, 27, 26, 27, 26, 27, 25, 26, 15, 22, 24, 12, 0, 14, 7, 24, 17, 24, 27, 27, 24, 27, 25, 26, 26, 28, 26, 25, 25, 29, 26, 25, 25, 26, 27],
				backgroundColor: 'rgba(0,121,193,.75)',
				borderColor: 'rgba(0, 121, 193, .3)',
				borderWidth: 3,
				fill: false,
			},{
                type: 'bar',
				label: 'Arrow 1',
				backgroundColor: 'rgba(248, 152, 29, .75)',
				data: [10, 9, 10, 10, 9, 10, 9, 9, 9, 9, 9, 9, 10, 9, 9, 9, 6, 0, 7, 7, 8, 9, 8, 9, 10, 9, 10, 9, 9, 9, 10, 10, 10, 9, 10, 9, 9, 9, 10, 10],
				borderColor: 'white',
				borderWidth: 0
			}, {
    			type: 'bar',
				label: 'Arrow 2',
				backgroundColor: 'rgba(38,188,215,.75)',
				data: [10, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 6, 7, 8, 6, 0, 7, 0, 8, 8, 8, 9, 9, 9, 9, 8, 9, 9, 9, 9, 8, 9, 10, 9, 8, 9, 9, 9],
			}, {
    			type: 'bar',
				label: 'Arrow 3',
                backgroundColor: 'rgba(113,112,116,.75)',
				data: [8, 8, 8, 9, 8, 8, 9, 8, 9, 8, 9, 7, 7, 0, 6, 7, 0, 0, 0, 0, 8, 0, 8, 9, 8, 6, 8, 8, 8, 8, 9, 7, 7, 7, 9, 8, 8, 7, 7, 8],
			}]
		},
		options: {
			scales: {
				yAxes: [{
					ticks: {
						beginAtZero :true
					},
					scaleLabel: {
    					display     : true,
    					labelString : 'Score',
					}, 
					stacked         : true,
				}],
				xAxes: [{
    				scaleLabel: {
        				display     : true,
        			    labelString : "End #"	
    				}, 
        				stacked     : true,
				}],
			},
			chartArea: {
                backgroundColor: ['rgba(240, 240, 240, 1)', 'rgba(255, 255, 255, 1)']
            },
            tooltips: {
                callbacks: { 
                    /*
                    label: function(tooltipItem, data) {
                        var label = data.datasets[tooltipItem.datasetIndex].label || '';
    
                        if (label) {
                            label += 'End #: ';
                        }
                        return label;
                    }*/
                    title: function(tooltipItem, data) {
                        console.log(tooltipItem, data);
                        var label = tooltipItem[0].xLabel
                        return "End #: " + label;
                        }
                }
            },
		}
	});
	
	// Arrow Chart 1
	var ctxac1 = document.getElementById("arrowChart1").getContext('2d');
	var doughnutChart = new Chart(ctxac1, {
		type: 'doughnut',
		data: {
				datasets: [{
					data: [9, 5, 12, 26, 53, 15],
					backgroundColor: [
						'rgba(255,99,132,1)',
						'rgba(109, 179, 63, 1)',
						'rgba(149,149,133,1)',
						'rgba(0,121,193,1)',
						'rgba(113,112,116,1)',
						'rgba(248, 152, 29, 1)'
					],
					label: 'Dataset 1'
				}],
				labels: ['0', '6', '7', '8', '9', '10']
			},
			options: {
				responsive: true
			}
	 
	});
	
	
	var ctxac2 = document.getElementById("arrowChart2").getContext('2d');
	var doughnutChart = new Chart(ctxac2, {
		type: 'doughnut',
		data: {
				datasets: [{
					data: [1, 1, 2, 2, 21, 13],
					backgroundColor: [
						'rgba(255,99,132,1)',
						'rgba(109, 179, 63, 1)',
                        'rgba(149,149,133,1)',
						'rgba(0,121,193,1)',
						'rgba(113,112,116,1)',
						'rgba(248, 152, 29, 1)'
					],
					label: 'Dataset 1'
				}],
				labels: ['0', '6', '7', '8', '9', '10']
			},
			options: {
				responsive: true
			}
	 
	});
	
	var ctxac3 = document.getElementById("arrowChart3").getContext('2d');
	var doughnutChart = new Chart(ctxac3, {
		type: 'doughnut',
		data: {
				datasets: [{
					data: [2, 2, 2, 7, 25, 2],
					backgroundColor: [
						'rgba(255,99,132,1)',
						'rgba(109, 179, 63, 1)',
						'rgba(149,149,133,1)',
						'rgba(0,121,193,1)',
						'rgba(113,112,116,1)',
						'rgba(248, 152, 29, 1)'
					],
					label: 'Dataset 1'
				}],
				labels: [0, 6, 7, 8, 9, 10],
			},
			options: {
				responsive: true
			}
	 
	});
	
	var ctxac4 = document.getElementById("arrowChart4").getContext('2d');
	var doughnutChart = new Chart(ctxac4, {
		type: 'doughnut',
		data: {
				datasets: [{
					data: [6, 2, 8, 17, 7,0],
					backgroundColor: [
						'rgba(255,99,132,1)',
						'rgba(109, 179, 63, 1)',
						'rgba(149,149,133,1)',
						'rgba(0,121,193,1)',
						'rgba(113,112,116,1)',
						'rgba(248, 152, 29, 1)'
					],
					label: 'Dataset 1'
				}],
				labels: [0,6,7,8, 9, 10],
			},
			options: {
				responsive: true
			}
	 
	});
	
		
	
	// comboBarLineChart
	/*
	var ctx2 = document.getElementById("comboBarLineChart").getContext('2d');
	var comboBarLineChart = new Chart(ctx2, {
		type: 'bar',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
			datasets: [{
					type: 'line',
					label: 'Dataset 1',
					borderColor: '#484c4f',
					borderWidth: 3,
					fill: false,
					data: [12, 19, 3, 5, 2, 3, 13, 17, 11, 8, 11, 9],
				}, {
					type: 'bar',
					label: 'Dataset 2',
					backgroundColor: '#FF6B8A',
					data: [10, 11, 7, 5, 9, 13, 10, 16, 7, 8, 12, 5],
					borderColor: 'white',
					borderWidth: 0
				}, {
					type: 'bar',
					label: 'Dataset 3',
					backgroundColor: '#059BFF',
					data: [10, 11, 7, 5, 9, 13, 10, 16, 7, 8, 12, 5],
				}], 
				borderWidth: 1
		},
		options: {
			scales: {
				yAxes: [{
					ticks: {
						beginAtZero:true
					}
				}]
			}
		}
	});	*/
			
	// pieChart
	var ctx3 = document.getElementById("pieChart").getContext('2d');
	var pieChart = new Chart(ctx3, {
		type: 'pie',
		data: {
				datasets: [{
					data: [12, 19, 3, 5, 2, 3],
					backgroundColor: [
						'rgba(255,99,132,1)',
						'rgba(54, 162, 235, 1)',
						'rgba(255, 206, 86, 1)',
						'rgba(75, 192, 192, 1)',
						'rgba(153, 102, 255, 1)',
						'rgba(255, 159, 64, 1)'
					],
					label: 'Dataset 1'
				}],
				labels: [
					"Red",
					"Orange",
					"Yellow",
					"Green",
					"Blue"
				]
			},
			options: {
				responsive: true
			}
	 
	});

	// doughnutChart
	var ctx4 = document.getElementById("doughnutChart").getContext('2d');
	var doughnutChart = new Chart(ctx4, {
		type: 'doughnut',
		data: {
				datasets: [{
					data: [12, 19, 3, 5, 2, 3],
					backgroundColor: [
						'rgba(255,99,132,1)',
						'rgba(54, 162, 235, 1)',
						'rgba(255, 206, 86, 1)',
						'rgba(75, 192, 192, 1)',
						'rgba(153, 102, 255, 1)',
						'rgba(255, 159, 64, 1)'
					],
					label: 'Dataset 1'
				}],
				labels: [
					"Red",
					"Orange",
					"Yellow",
					"Green",
					"Blue"
				]
			},
			options: {
				responsive: true
			}
	 
	});

	// radarChart
	var ctx5 = document.getElementById("radarChart").getContext('2d');
	var doughnutChart = new Chart(ctx5, {
		type: 'radar',
		data: {
				labels: [["Eating", "Dinner"], ["Drinking", "Water"], "Sleeping", ["Designing", "Graphics"], "Coding", "Running"],
				datasets: [{
					label: "My First dataset",
					backgroundColor: 'rgba(255, 99, 132, 0.2)',
					borderColor: 'rgba(255,99,132,1)',
					pointBackgroundColor: 'red',
					data: [12, 19, 13, 11, 19, 17]
				}, {
					label: "My Second dataset",
					backgroundColor: 'rgba(250, 80, 112, 0.3)',
					borderColor: 'rgba(54, 162, 235, 1)',
					pointBackgroundColor: 'blue',
					data: [15, 12, 14, 15, 9, 11]
				},]
			},
			options: {
				responsive: true
			}
	 
	});

	// polarAreaChart
	var ctx6 = document.getElementById("polarAreaChart").getContext('2d');
	var doughnutChart = new Chart(ctx6, {
		type: 'polarArea',
		data: {
			labels: ["Red","Green","Yellow","Grey","Blue"],
			datasets: [{
				label: "My First Dataset",
				data: [11,16,7,3,14],
				backgroundColor: ["rgb(255, 99, 132)","rgb(75, 192, 192)","rgb(255, 205, 86)","rgb(201, 203, 207)","rgb(54, 162, 235)"]
				}]
		}
    });
});