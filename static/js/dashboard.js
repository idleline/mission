$(document).ready(function() {
    /* Default RGB Colors
		"rgb(255, 99, 132)",
		"rgb(75, 192, 192)",
		"rgb(255, 205, 86)",
		"rgb(171, 203, 60)", 
		"rgb(54, 162, 235)", 
		"rgb(255,172,64)"
    */
    
    // ROW 1 Charts on Dashboard - Charts    
    $.ajax({
        url         : "/api/selectors/chart",
        type        : "GET",
        contentType : "application/json",
        dataType    : "json",
    }).done(function (d) {
        var ctx1 = document.getElementById("dkimSelectorRecordChart").getContext('2d');
    	var doughnutChart = new Chart(ctx1, {
    		type: 'pie',
    		data: {
    			labels: d.data.labels,
    			datasets: [{
    				label: "DKIM Selector Records",
    				data: d.data.count,
    				backgroundColor: [
                    "rgb( 0, 69,  124)",
                    "rgb(109, 179, 63)",
                    "rgb(38, 188, 215)",
                    "rgb(248, 152, 29)",
                    "rgb(241, 95, 124)",
                    "rgb( 0, 121, 193)",
                    "rgb(179,  35, 23)",
    				]
                }]
    		}
        });
    });
    
    $.ajax({
        url         : "/api/selectorips/chart",
        type        : "GET",
        contentType : "application/json",
        dataType    : "json",
    }).done(function (chart) {
        //console.log(chart.data);
        var ctx2 = document.getElementById("dkimIPChart").getContext('2d');
    	var doughnutChart = new Chart(ctx2, {
    		type: 'pie',
    		data: {
    			labels: chart.data.labels,
    			datasets: [{
    				label: "DKIM Unique IPs",
    				data: chart.data.count,
    				backgroundColor: [
    				"rgb(255, 205, 86)",
    				"rgb(75, 192, 192)",
    				"rgb(171, 203, 60)",
    				"rgb(255, 99, 132)",    				 
    				"rgb(54, 162, 235)", 
    				"rgb(255,172,64)"
                    ]
                }]
    		}
        });
    });
    
    $.ajax({
        url         : "/api/headerfrom/chart",
        type        : "GET",
        contentType : "application/json",
        dataType    : "json",
    }).done(function (chart) {
        //console.log(chart.data);
        var ctx3 = document.getElementById("headerFromRecordChart").getContext('2d');
    	var doughnutChart = new Chart(ctx3, {
    		type: 'pie',
    		data: {
    			labels: chart.data.labels,
    			datasets: [{
    				label: "Header From Usage",
    				data: chart.data.count,
    				backgroundColor: [
    				"rgb(171, 203, 60)", 
    				"rgb(75, 192, 192)",
    				"rgb(255, 205, 86)",
    				"rgb(54, 162, 235)", 
    				"rgb(255,172,64)",
    				"rgb(255, 99, 132)",    				
    				]
                }]
    		}
        });
    });
    
    
    // ROW 2 Charts 
    $.ajax({
        url         : "/api/spffail/chart",
        type        : "GET",
        contentType : "application/json",
        dataType    : "json",
    }).done(function (chart) {
        console.log(chart.data);
        var ctx4 = document.getElementById("SPFFailChart").getContext('2d');
    	var doughnutChart = new Chart(ctx4, {
    		type: 'bar',
    		data: {
    			labels: chart.data.labels,
    			datasets: [{
        			type: 'bar',
    				label: "Fail",
    				data: chart.data.results.fail,
    				backgroundColor: "rgb(75, 192, 192)"
                },
                {
    				type: 'bar',
    				label: "Pass",
    				data: chart.data.results.pass,
    				backgroundColor: "rgb(255, 99, 132)",
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
        					labelString : 'Something',
    					}, 
    					stacked         : true,
    				}],
    				xAxes: [{
        				scaleLabel: {
            				display     : true,
            			    labelString : "IDK"	
        				}, 
            				stacked     : true,
    				}],
			    }
            }
        });
    });

    $.ajax({
        url         : "/api/domainspffail/chart",
        type        : "GET",
        contentType : "application/json",
        dataType    : "json",
   
    }).done(function (chart) {
        
        var ctx5 = document.getElementById("DomainSPFFailChart").getContext('2d');
    	var doughnutChart = new Chart(ctx5, {
    		type: 'bar',
    		data: {
    			labels: chart.data.labels,
    			datasets: [{
        			type: 'bar',
    				label: "Domain SPF Failures",
    				data: chart.data.count,
    				backgroundColor: [
    				"rgb(255, 99, 132)",
    				"rgb(75, 192, 192)",
    				"rgb(255, 205, 86)",
    				"rgb(171, 203, 60)", 
    				"rgb(54, 162, 235)", 
    				"rgb(255,172,64)"
    				]
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
        					labelString : 'Something',
    					}, 
    					stacked         : true,
    				}],
    				xAxes: [{
        				scaleLabel: {
            				display     : true,
            			    labelString : "IDK"	
        				}, 
            				stacked     : true,
    				}],
			    },
            }
        });
    });

    $.ajax({
        url         : "/api/topips/chart",
        type        : "GET",
        contentType : "application/json",
        dataType    : "json",
    }).done(function (chart) {
        //console.log(chart.data);
        var ctx6 = document.getElementById("topIPsChart").getContext('2d');
    	var pieChart = new Chart(ctx6, {
    		type: 'pie',
    		data: {
    			labels: chart.data.labels,
    			datasets: [{
    				label: "Top 10 IPs",
    				data: chart.data.count,
    				backgroundColor: [
    				"rgb(171, 203, 60)", 
    				"rgb(75, 192, 192)",
    				"rgb(255, 205, 86)",
    				"rgb(54, 162, 235)", 
    				"rgb(255,172,64)",
    				"rgb(255, 99, 132)",    				
    				]
                }]
    		}
        });
    });				
});
