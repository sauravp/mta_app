
var prev_data = null;           // remember data fetched last time
var waiting_for_update = false; // are we currently waiting?
var LONG_POLL_DELAY = 5000; // how long should we wait? (msec)


/**
 * Load data from /data,
 */
function load_data() {
    $.ajax({ url: '/data',
             success: function(data) {
                          display_data(data);
                          wait_for_update();
                      },
    });
    return true;
}


/**
 * Uses separate update notification and data providing URLs. Could be combined, but if
 * they're separated, the Python routine that provides data needn't be changed from
 * what's required for standard, non-long-polling web app. If they're combined, arguably
 * overloads the purpose of the function.
 */
function wait_for_update() {
    if (!waiting_for_update) {
        waiting_for_update = true;
        $.ajax({ url: '/updated',
                 success:  load_data,        // if /updated signals results ready, load them!
                 complete: function () {
                    waiting_for_update = false;
                    wait_for_update(); // if the wait_for_update poll times out, rerun
                 },
                 timeout:  LONG_POLL_DELAY,
               });
    }
}


/**
 * show the data acquired by load_data()
 */
function display_data(data) {
    // console.log("data.time:", data.time_loaded, "data.status:", data.status);
    if (data && (data != prev_data)) {      // if there is data, and it's changed

        // update the contents of several HTML divs via jQuery
        $('div#time').html(data.time_loaded);
        $('div#status').html(data.status);

        // remember this data, in case want to compare it to next update
        prev_data = data;

        // a little UI sparkle - show the #updated div, then after a little
        // while, fade it away
        $('#updated').fadeIn('fast');
        setTimeout(function() {  $('#updated').fadeOut('slow');  }, 2500);
    }
}

/**
 * Initial document setup - hide the #updated message, and provide a
 * "loading..." message
 */
$(document).ready(function() {
    $('div#updated').fadeOut(0);

    // load the initial data (assuming it will be immediately available)
    load_data();
});