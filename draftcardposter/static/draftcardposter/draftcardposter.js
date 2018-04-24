var picks;

$(document).ready(function() {
    $.getJSON('picks', function(data) {
        picks = data.picks[data.current_year];
        for (var i=1; i <= picks.length; i++) {
            $("#round").append($('<option>', { value: i, text: i }));
        }
    }).done(function() {
        $("#round").selectpicker('refresh');
        $("#round").on("changed.bs.select",
            function(e, clickedIndex, newValue, oldValue) {
                console.log(this.value, clickedIndex, newValue, oldValue);
                $("#pick").find('option').remove();
                var round = picks[this.value - 1];
                for (var i=0; i < round.length; i++) {
                    var pick = round[i];
                    var text = pick[0];
                    if (pick[1] == "c") text += " (comp)";
                    $("#pick").append($('<option>', { value: pick[0], text: text}));
                }
                $("#pick").selectpicker('refresh');
            }
        )
    });
    $.getJSON('players', function(data) {
        $("#name").autocomplete({
            minLength: 2,
            source: $.map(data.players, function (p) {
                return {value: p.name, label: p.name + " ("+p.position+"), " + p.college, obj: p};
            }),
            focus: function(event, ui) {
                $("#name").val(ui.item.value);
                $("#college").val(ui.item.obj.college);
                $("#position").selectpicker('val', ui.item.obj.position);
            },
            select: function(event, ui) {
                $("#name").val(ui.item.value);
                $("#college").val(ui.item.obj.college);
                $("#position").selectpicker('val', ui.item.obj.position);
            }
        });
    });
});
