$(document).ready(function() {
			// data-tables
	$('#example1').DataTable();
			
	// counter-up
	$('.counter').counterUp({
		delay: 10,
		time: 600
	});
			
    var ctx1 = document.getElementById("lineChart").getContext('2d');
	var lineChart = new Chart(ctx1, {
		type: 'bar',
		data: {
			labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
			datasets: [{
					label: 'Dataset 1',
					backgroundColor: '#3EB9DC',
					data: [10, 14, 6, 7, 13, 9, 13, 16, 11, 8, 12, 9] 
				}, {
					label: 'Dataset 2',
					backgroundColor: '#EBEFF3',
					data: [12, 14, 6, 7, 13, 6, 13, 16, 10, 8, 11, 12]
				}]
				
		},
		options: {
						tooltips: {
							mode: 'index',
							intersect: false
						},
						responsive: true,
						scales: {
							xAxes: [{
								stacked: true,
							}],
							yAxes: [{
								stacked: true
							}]
						}
					}
	});

	var ctx2 = document.getElementById("pieChart").getContext('2d');
	var pieChart = new Chart(ctx2, {
		type: 'pie',
		data: {
				datasets: [{
					data: [12, 19, 3, 5, 2, 3],
					backgroundColor: [
						'rgba(0,69,124,1)',
						'rgba(0,121,193,1)',
						'rgba(149,149,133,1)',
						'rgba(113,112,116,1)',
						'rgba(0,124,133,1)',
						'rgba(38,188,215,1)'
					],
					label: 'Dataset 1'
				}],
				labels: [
					"Dark Blue",
					"Light Blue",
					"Sand",
					"Slate",
					"Sea",
					"Aqua",
				]
			},
			options: {
				responsive: true
			}
	 
	});

	var ctx3 = document.getElementById("doughnutChart").getContext('2d');
	var doughnutChart = new Chart(ctx3, {
		type: 'doughnut',
		data: {
				datasets: [{
					data: [12, 19, 3, 5, 2, 3],
					backgroundColor: [
						'rgba(0,69,124,1)',
						'rgba(0,121,193,1)',
						'rgba(149,149,133,1)',
						'rgba(113,112,116,1)',
						'rgba(0,124,133,1)',
						'rgba(38,188,215,1)'
					],
					label: 'Dataset 1'
				}],
				labels: [
					"Dark Blue",
					"Light Blue",
					"Sand",
					"Slate",
					"Sea",
					"Aqua",
				]
			},
			options: {
				responsive: true
			}
	 
	});
	
	$('.notify-details').on('click', function (event) {
        var notifyId = $(this)[0].id;
        var jData = {
            'alert_id'      : notifyId,
            'action'        : 'read',
        }


        $.ajax({
            url         : '/user/alert',
            type        : 'POST',
            data        : JSON.stringify(jData),
            contentType : 'application/json',
            dataType    : 'json',
            encode      : true,
            success     : function(e) {
                console.log(data);
                }
            });
        
        event.preventDefault()
	});
} );