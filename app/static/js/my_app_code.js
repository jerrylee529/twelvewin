var $td = null;

function editInfo(obj){
    $td= $(obj).parents('tr').children('td');
    var paramName = $td.eq(2).text();
    var paramCode = $td.eq(1).text();
    var paramLabels = $td.eq(10).text();

    //向模态框中传值
    $('#code').text(paramCode)

    $('#labels').val(paramLabels);
    
    $('#myModal').modal('show');
}

//提交更改
function update() {
    //获取模态框数据
    var code = $('#code').text();
    var labels = $('#labels').val();
    
    if ($td != null) {
        $td.eq(10).text(labels);
    }
    /* 
    $.ajax({
        type: "post",
	url: "/dataFromAjax",
	data: "code=" + code + "&labels=" + labels,
	dataType: 'json',
	success: function(result) {
            $('#myModal').modal('hide'); 
	}
    });
    */
    $.post("/dataFromAjax", {"code":code,"labels":labels}, function(data){
        $('#myModal').modal('hide');
    },"json"); 
}

function filterInfo(){

    $('filterModal').modal('show');
}

//提交过滤
function filter() {
    //获取模态框数据
    var labels = $('#labels').val();

    
}



//删除行;(obj代表连接对象)
function removeParam(obj) {
    alert("delte tr");
    var $td= $(obj).parents('tr').children('td');
    var paramName = $td.eq(0).text();
    var paramCode = $td.eq(1).text();
    //在js端删除一整行数据
    $(obj).parent().parent().remove();
}

