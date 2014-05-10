
$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#messageform").live("submit", function() {
	    newMessage( $('#input').val() );
	    return false; // make form not submit
    });

    $(document).bind("keydown", bindarrows );

    // snap cards to map.. kind of annoying
    //$('.cardsprite').draggable( {snap:'.map'});

    $('.map').droppable({
            accept: '.cardsprite',
            drop: function( event, ui) {

                newMessage( 'play ' + $(ui.draggable).attr('slot') +' ' + $(this).attr('id'))
                }
        });



    updater.poll();
});


function newMessage (cmd) {
    $.post( '/send', {'input':cmd}, function( response) 
        {
            true
            // re-enable sending or something
        });
    };


function bindarrows(e) {

    switch ( e.keyCode) {

		case 13:
			newMessage($('#input').val());
			return false;

		// annoying, up and down trigger firefox features

		case 37:
            newMessage( 'west');
			return false;
		case 38:
            newMessage( 'north');
			return false;
		case 39:
            newMessage( 'east');
			return false;
		case 40:
            newMessage( 'south');
			return false;

	    }};


var updater = {
    errorSleepTime: 500,

    poll: function() {
	$.ajax({
        url: "/recv", 
        type: "GET",
        dataType: "json", 
        success: updater.onSuccess,
		error: updater.onError
        });
    },

    onSuccess: function(response) {
        if (response==null) { return self.onError() };
	    try {
            for (line in response) {
                // console.log( response[line]);
                eval( response[line]);
                $("body").scrollTo('100%', {'axis':'y'});
                $('#input').select();
                }
    	    } catch (e) {
            console.log(e)
    	    updater.onError();
    	    return;
    	    }
    	updater.errorSleepTime = 500;
    	window.setTimeout(updater.poll, 0);
        },

    onError: function(response) {
    	updater.errorSleepTime *= 2;
    	// console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
    	window.setTimeout(updater.poll, updater.errorSleepTime);
        },
    };
