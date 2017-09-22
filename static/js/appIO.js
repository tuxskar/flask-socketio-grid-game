/**
 * Created by tuxskar on 4/24/17.
 */
$(document).ready(function () {

    var rows,
        columns,
        $grid = $('.grid'),
        itemHeight, itemWidth;


    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var namespace = '/grid-game';
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);


    var currentUserId;

    /**
     * Initializing this user
     */
    socket.on('message', function (data) {
        if (data.userId) currentUserId = data.userId;
        if (data.symbol) $('#symbol').text(data.symbol);
        if (data.gridDimension) {
            var marginPx = 4;
            $grid.empty();
            columns = data.gridDimension[0];

            rows = data.gridDimension[1];
            itemHeight = ($grid.height() / rows) - marginPx;
            itemWidth = ($grid.width() / columns) - marginPx;

            for (var i = 0; i < rows; i++) {
                for (var j = 0; j < columns; j++) {
                    $grid.append($('<div/>').addClass('item').css({
                        height: itemHeight,
                        width: itemWidth,
                        "line-height": itemHeight + 'px'
                    }))
                }
            }
        }
    });

    /**
     * Updating the connected users
     */
    socket.on('users_connected', function (lenUsers) {
        $('#user-cnt').text(lenUsers)
    });


    /**
     * Updating a user position
     */
    socket.on('user_position', function (data) {
        var userId = data.userId;

        if (data.remove) {
            // Deleting the actual position if any
            updateGridPosition('no-pos', 'no-symbol', userId, 'remove');
            return
        }

        var newPosition = data.pos,
            symbol = data.symbol;

        // Deleting the actual position if any
        updateGridPosition('no-pos', 'no-symbol', userId, 'remove');

        // adding the new position of the item
        updateGridPosition(newPosition, symbol, userId);
    });

    /**
     * Getting the whole grid status, usually to initialize it
     */
    socket.on('grid_status', function (grid) {
        Object.keys(grid).forEach(function (userId) {
            var userInfo = grid[userId],
                userPos = userInfo.pos,
                userSymbol = userInfo.symbol;
            updateGridPosition(userPos, userSymbol, userId);
        });
    });

    /**
     * Updating a cell in the grid based on the parameters
     * @param position: list of 2 elements, [X,Y], starting on 1,1
     * @param symbol: string with the symbol representing this cell
     * @param positionUserId: userId that owns the position we need to move
     * @param remove: if some value is here, the position will be removed
     */
    function updateGridPosition(position, symbol, positionUserId, remove) {
        var currentUserClass = (currentUserId === positionUserId ? 'current-user-item' : 'other-user-item');
        if (remove) {
            var $positionItem = $('#' + positionUserId),
                $parent = $positionItem.parent();
            $positionItem.remove();
            var $otherItems = $parent.find('div');

            $parent.removeClass('current-user-item other-user-item');
            if ($otherItems.length > 0) {
                var currentUserHere = $otherItems.find('#' + currentUserId).length > 0,
                    newClass = 'other-user-item';
                if (currentUserHere) {
                    newClass = 'current-user-item';
                }
                $parent.addClass(newClass);
            }
            return
        }
        var posX = position[0], posY = position[1],
            // converting from the position in X, Y to the position in the list of cells in the grid
            gridPosition = ((posY - 1) * columns) + (posX - 1),
            $newCell = $('<div/>').text(symbol).attr({'id': positionUserId});
        $grid.find('.item:eq(' + gridPosition + ')').addClass(currentUserClass).append($newCell)
    }

    $('#btn-up').on('click', function (e) {
        makeMove('up');
    });
    $('#btn-down').on('click', function (e) {
        makeMove('down');
    });
    $('#btn-left').on('click', function (e) {
        makeMove('left');
    });
    $('#btn-right').on('click', function (e) {
        makeMove('right');
    });

    function makeMove(direction) {
        socket.emit('movement', {direction: direction});
    }

    $(document).keydown(function (e) {
        switch (e.which) {
            case 37: // left
                makeMove('left');
                break;

            case 38: // up
                makeMove('up');
                break;

            case 39: // right
                makeMove('right');
                break;

            case 40: // down
                makeMove('down');
                break;

            default:
                return; // exit this handler for other keys
        }
        e.preventDefault(); // prevent the default action (scroll / move caret)
    });


});