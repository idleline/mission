$(document).ready(function () {     
    // Nav highlighting
    var w = window.location.pathname.split('/')[1]; 
    var p = $('nav').find('a[href="/'+w+'"]').parent().attr('class', 'active');
    
    // Enable use of Bootstrap messaging
    statusMsg = function(d, s) {
        if ( Array.isArray(d.message) ) {
            var message = d.message.join(' ');
            console.log(d.message, message);
        }
        else {
            var message = d.message;
        }
        
        $('#messages').append('<div class="alert alert-'+s+' alert-dismissible fade in" data-dismiss="alert" role="alert">'
        +'<center>'+message+'</center></div>');
    }
        
    // Input box error messaging
    zhErrMsg = function(d) {
        if ( Array.isArray(d.message) ) {
            var message = d.message.join(' ');
            console.log(d.message, message);
        }
        else {
            var message = d.message;
        }

        $('#host-search').addClass('has-error');
        $('#host-input').after("<span id='host-input-err' class='has-error'>"+message+"</span>");
    }
    
    // Draw Spinner & hide 
    $('body').append('<div id="circle" class="spinner"></div>');
    var spinner = $('#circle').hide()  // Hide it initially
    
    // Show spinner on AJAX calls
    $(document)
        .ajaxStart(function(event) {
            $('article').addClass('blur-filter');
            spinner.show();
        })
        .ajaxStop(function(event) {
            $('article').removeClass('blur-filter');
            spinner.hide();
        });    
    
    // Add jQuery listener to notifications for read 
    $('body').on('click', 'li.notification-list-item', function (event) {
        event.preventDefault()
        rn($(this)[0].id);
    });
    
    // Function to retrieve notifications for current user
    zoneNotify = function () {
        $.ajax({
            url     : '/user/notifications',
            type    : 'POST',
        })
        .done(function(data) {
            if (data.status == 'error' ) {
                statusMsg(data, 'danger')
            }
            else {
                if ( data.hasOwnProperty('notifications') ) {
                    notifications = data.notifications;
                } else {
                    notifications = new Array(0);
                }
                if (data.count == 0) {
                    $('#notify-counter').html('');
                }
                else {
                    $('#notify-counter').html(data.count);
                }
                
                if ( notifications.length > 5 ) {
                    var n = 6;
                }
                else {
                    var n = notifications.length;
                }
                
                for ( i = 0; i < n; i++ ) {
                    var notice = notifications[i];
                    var nid = 'notice-'+notice.id

                    $('.notifications-container').append('<li id="'+nid+'" class="notification-list-item"><div class="notification-item"><div class="body-col"><div class="img-col">'
                    +'<div class="img" style="background-image: url('+notice.avatar+')"></div></div><p><span class="accent">'+notice.creator+'</span> '
                    +notice.title+'<span class="accent"> '+notice.content+'</span>. </p></div></div></li>');
                }
            }
        });
    }
    
    // Function to call server for read notification
    rn = function (n) {
        $.ajax({
            url     : '/user/notifications/read/'+n,
            type    : 'POST',
        })
        .done(function(data) {
            if (data.status == 'error' ) {
                statusMsg(data, 'danger')
            }
            else {
                $('.notifications-container').empty();
                zoneNotify()
            }
        });
    }
    
    objectifyForm = function(formArray) { 
        var returnArray = {};
        for (var i = 0; i < formArray.length; i++){
            returnArray[formArray[i]['name']] = formArray[i]['value'];
        }
    return returnArray;
    }
    
    // Call function to retrieve notifications     
    zoneNotify()
});