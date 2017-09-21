/**
 * Created by tuxskar on 9/22/17.
 */

$(document).ready(function () {
    var options = ['btn-up', 'btn-down', 'btn-left', 'btn-right'],
        timeoutFunc,
    maxTimeWait = userMaxTimeWait, minTimeWait = 100;

    function makeMove() {
        var optionIdx = Math.floor((Math.random() * options.length));
        $('#' + options[optionIdx]).click();
    }

    function callToMove() {
        makeMove();
        timeoutFunc = setTimeout(function () {
                callToMove();
            }
            , Math.floor((Math.random() * maxTimeWait) + minTimeWait)
        );
    }
    callToMove();
});