/* js rendering instructions to push the deck */


$('#deck').css( "visibility", "visible");
$('#deck').dialog( {'modal':true, 'minWidth':500} );

$('#everything').children().remove()
$('#inventory').children().remove()
$('#equipped').children().remove()

$('#everything').append( '<h2>Deck</h2>')
$('#inventory').append( '<h2>Inventory</h2>')
$('#equipped').append( '<h2>Equipped</h2>')

{% for card in Cards %}
    $('#everything').append( '<li><img class="cardsprite" src="/static/cards/{{card}}.jpg" /> </li>')
{% end %}

{% for card in inventory %}
    $('#inventory').append( '<li>{{card}}</li>')
{% end %}

{% for slot in equipped %}
    $('#equipped').append( '<li>{{equipped[slot]}}</li>')
{% end %}
    

// $('#deck').
