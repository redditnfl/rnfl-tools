$(document).ready(function() {
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
