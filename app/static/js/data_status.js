(function ($) {
    function jobStatusText(job) {
        if (!job) {
            return "未记录";
        }
        if (job.status === "success") {
            return "成功 (" + (job.finished_at || "") + ")";
        }
        if (job.status === "failed") {
            return "失败 (" + (job.finished_at || "") + ")";
        }
        if (job.status === "running") {
            return "运行中";
        }
        return job.status;
    }

    function fileUpdateText(fileInfo) {
        if (!fileInfo || !fileInfo.exists) {
            return "无数据";
        }
        return fileInfo.update_time || "未知";
    }

    function renderStatus(data) {
        var rankings = (data.files && data.files.rankings) || {};
        var technical = (data.files && data.files.technical) || {};
        var eodJob = data.jobs && data.jobs.eod_all;
        var dailyJob = data.jobs && data.jobs.daily_pipeline;
        var rankingJob = data.jobs && data.jobs.ranking_pipeline;

        var parts = [
            "市盈率排名: " + fileUpdateText(rankings.pe),
            "历史新高: " + fileUpdateText(technical.highest_in_history),
            "日终汇总: " + jobStatusText(eodJob),
            "日终任务: " + jobStatusText(dailyJob),
            "排名任务: " + jobStatusText(rankingJob)
        ];

        return parts.join(" · ");
    }

    $(function () {
        var $footer = $("#data-status-footer");
        if ($footer.length === 0) {
            return;
        }

        $.getJSON("/main/data_status")
            .done(function (data) {
                $footer.text(renderStatus(data));
            })
            .fail(function () {
                $footer.text("数据状态暂不可用");
            });
    });
}(jQuery));
