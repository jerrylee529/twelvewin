/**
 * Created by Administrator on 2018/7/9.
 */
var $td = null;
var curr_index = null;

function editLabel(obj, index) {
    $td = $(obj).parents('tr').children('td');
    var paramName = $td.eq(2).text();
    var paramCode = $td.eq(1).text();
    var paramLabels = $td.eq(13).text();

    curr_index = index;

    //向模态框中传值
    $('#stock_code').text(paramCode)

    $('#stock_name').text(paramName)

    $('#labels').val(paramLabels);

    $('#myModal').modal('show');
}

function chart_formatter(value, row, index) {
    var d = '<a href="#" mce_href="#" onclick="show(\'' + row.code + '\',\'' + row.name + '\')">' + value + '</a> ';
    return d;
}

function labels_formatter(value, row, index, field) {
    var a = null;
    if (row.labels == null || row.labels == "")
        a = '<a href="#" mce_href="#" onclick="editLabel(this,' + index + ')"><span class="glyphicon glyphicon-pencil"></span></a>'
    else
        a = '<a href="#" mce_href="#" onclick="editLabel(this,' + index + ')">' + row.labels + '</a>'
    return a;
}

function operations_formatter(value, row, index, field) {
    var b = '<a href="#" mce_href="#" onclick="deleteItem(this,' + index + ')"><span class="glyphicon glyphicon-minus"></span></a> ';
    return b;
}

$(function () {
    $('#updateButton').click(function () {
        var code = $('#stock_code').text();
        var labels = $('#labels').val();

        $('#table').bootstrapTable('updateCell', {
            index: curr_index,
            field: 'labels',
            value: labels
        });

        $.post("/self_selected_stock/update_labels", {"code": code, "labels": labels}, function (data) {
            $('#myModal').modal('hide');
        }, "json");

    });
})


function deleteItem(obj, index) {
    $td = $(obj).parents('tr').children('td');
    var paramCode = $td.eq(1).text();

    if (confirm('确认删除自选?')) {
        $.post("/self_selected_stock/delete", {"code": paramCode}, function (data) {
            $('#table').bootstrapTable('remove', {
                field: 'code',
                values: [paramCode]
            });
        }, "json");
    }
}

function show(code, name) {
    $('#instrument').html('<span class="label label-primary">' + code + '</span><span class="label label-info">' + name + '</span>');

    $('#chartModel').modal('show');

    show_chart(code)
}
