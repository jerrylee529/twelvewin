/**
 * Created by Administrator on 2018/7/9.
 */
(function () {
    function init(table,url,params,titles,formatters,hasCheckbox,toolbar) {
        $(table).bootstrapTable({
            url: url,                           //请求后台的URL（*）
            method: "get",
            dataType: "json",
            pagination: true, //前端处理分页
            singleSelect: false,//是否只能单选
            search: false, //显示搜索框，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
            toolbar: toolbar, //工具按钮用哪个容器
            cache: false, //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
            pageNumber: 1, //初始化加载第10页，默认第一页
            pageSize: 20, //每页的记录行数（*）
            pageList: [10, 20, 50, 100], //可供选择的每页的行数（*）
            strictSearch: true,//设置为 true启用 全匹配搜索，false为模糊搜索
            showColumns: true, //显示内容列下拉框
            showRefresh: true, //显示刷新按钮
            minimumCountColumns: 2, //当列数小于此值时，将隐藏内容列下拉框
            clickToSelect: true, //设置true， 将在点击某行时，自动勾选radiobox 和 checkbox
            uniqueId: "id", //每一行的唯一标识，一般为主键列
            cardView: false, //是否显示详细视图
            sidePagination: "client", //分页方式：client客户端分页，server服务端分页（*）
            responseHandler: function(data){
                window.jsonData = data;
                return data.rows;
            },

            queryParams: function(params) {
                params["labels"] = $("#filterLabels").val();
                return params;
            },

            formatLoadingMessage: function(){
                return "请稍等，正在加载中。。。";
            },

            formatNoMatches: function(){
                return "没有相关的匹配结果";
            },

            columns: createCols(params,titles,formatters,hasCheckbox)
        });
    }

    function createCols(params,titles,formatters,hasCheckbox) {
        if(params.length!=titles.length)
            return null;
        var arr = [];
        if(hasCheckbox) {
            var objc = {};
            objc.checkbox = true;
            arr.push(objc);
        }
        for(var i = 0;i<params.length;i++) {
            var obj = {};
            obj.field = params[i];
            obj.title = titles[i];
            if (formatters[i] != null) {
                obj.formatter = formatters[i];
            }
            obj.align = 'center';
            obj.sortable = 'true';
            arr.push(obj);
        }
        return arr;
    }

    //可发送给服务端的参数：limit->pageSize,offset->pageNumber,search->searchText,sort->sortName(字段),order->sortOrder('asc'或'desc')
    function queryParams(params) {
        return {   //这里的键的名字和控制器的变量名必须一直，这边改动，控制器也需要改成一样的
            limit: params.limit,   //页面大小
            offset: params.offset  //页码
            //name: $("#txt_name").val()//关键字查询
        };
    }

    // 传'#table'
    createBootstrapTable = function (table,url,params,titles,formatters,hasCheckbox,toolbar) {
        init(table,url,params,titles,formatters,hasCheckbox,toolbar);
    }

})();
