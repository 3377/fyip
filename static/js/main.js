// 工具函数
function loadBusuanziScript() {
    $.getScript("//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js", function () {
        setTimeout(function () {
            if ($("#busuanzi_value_site_pv").text() === "") {
                $("#busuanzi_value_site_pv").text("无法获取");
            }
            if ($("#busuanzi_value_site_uv").text() === "") {
                $("#busuanzi_value_site_uv").text("无法获取");
            }
        }, 3000);
    });
}

function createInfoItem(label, value) {
    return '<div class="info-row"><span class="info-label">' + label + ':</span><span class="info-value">' + value + "</span></div>";
}

function updateTime() {
    const now = new Date();
    const utcTime = now.getTime() + now.getTimezoneOffset() * 60000;

    // 北京时间 (UTC+8)
    const beijingTime = new Date(utcTime + 8 * 3600000);
    $("#beijingTime").text(formatDate(beijingTime));

    // UTC时间
    const utc = new Date(utcTime);
    $("#utcTime").text(formatDate(utc));

    // 美东时间 (UTC-4/UTC-5)
    const usOffset = isDST() ? -4 : -5;
    const usTime = new Date(utcTime + usOffset * 3600000);
    $("#usTime").text(formatDate(usTime));
}

function isDST() {
    const today = new Date();
    const year = today.getFullYear();
    const march = new Date(year, 2, 1);
    const november = new Date(year, 10, 1);

    const secondSundayInMarch = new Date(march.setDate(14 - march.getDay()));
    const firstSundayInNovember = new Date(november.setDate(7 - november.getDay()));

    return today >= secondSundayInMarch && today < firstSundayInNovember;
}

function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");

    if (window.innerWidth <= 768) {
        return `${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

// 显示IP信息
function displayResult(ip, info) {
    $("#result").empty();

    var content = "";
    content += createInfoItem("您的IP", createCopyableValue(ip, ip));
    content += createInfoItem("大洲", createCopyableValue(info.continent, info.continent || "-"));
    content += createInfoItem("国家", createCopyableValue(info.country, info.country || "-"));
    content += createInfoItem("省份", createCopyableValue(info.prov, info.prov || "-"));
    content += createInfoItem("城市", createCopyableValue(info.city, info.city || "-"));
    content += createInfoItem("区县", createCopyableValue(info.district, info.district || "-"));
    content += createInfoItem("运营商", createCopyableValue(info.isp, info.isp || "-"));
    content += createInfoItem("ASN码", createCopyableValue(info.asn, info.asn || "-"));
    content += createInfoItem("行政码", createCopyableValue(info.adcode, info.adcode || "-"));
    content += createInfoItem("时区", createCopyableValue(info.timezone, info.timezone || "-"));
    content += createInfoItem("纬度", createCopyableValue(info.lat, info.lat || "-"));
    content += createInfoItem("经度", createCopyableValue(info.lng, info.lng || "-"));
    content += createInfoItem("位置A", createCopyableValue(info.location_a, info.location_a || "-"));
    content += createInfoItem("位置B", createCopyableValue(info.location_b, info.location_b || "-"));
    content += createInfoItem("位置C", createCopyableValue(info.location_c, info.location_c || "-"));
    content += createInfoItem("位置D", createCopyableValue(info.location_d, info.location_d || "-"));
    content += createInfoItem("北京时间", '<span id="beijingTime"></span>');
    content += createInfoItem("UTC时间", '<span id="utcTime"></span>');
    content += createInfoItem("美东时间", '<span id="usTime"></span>');
    content += createInfoItem("访问总数", '<span id="busuanzi_value_site_pv">-</span>');
    content += createInfoItem("访客总数", '<span id="busuanzi_value_site_uv">-</span>');

    $("#result").html(content);
    loadBusuanziScript();

    // 更新时间显示
    if (window.timeInterval) {
        clearInterval(window.timeInterval);
    }
    updateTime();
    window.timeInterval = setInterval(updateTime, 1000);
}

// 创建可复制的值
function createCopyableValue(value, displayValue) {
    if (value === '-' || !value) {
        return '-';
    }
    return `<span class="copyable-value" onclick="window.copyValue(event, '${value}')">${displayValue}<span class="copy-tooltip">已复制!</span></span>`;
}

// 复制值到剪贴板
window.copyValue = function (event, value) {
    const element = event.currentTarget;
    const tooltip = element.querySelector('.copy-tooltip');
    
    // 尝试使用现代的 Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value)
            .then(showCopySuccess)
            .catch(() => fallbackCopy(value, showCopySuccess));
    } else {
        // 如果 Clipboard API 不可用，使用后备方案
        fallbackCopy(value, showCopySuccess);
    }

    function showCopySuccess() {
        // 计算提示框位置
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.top - 30) + 'px';
        
        // 显示提示
        tooltip.style.display = 'block';
        
        // 1.5秒后隐藏
        setTimeout(() => {
            tooltip.style.display = 'none';
        }, 1500);
    }
};

// 复制文本的后备方案
function fallbackCopy(text, callback) {
    try {
        // 创建临时文本区域
        const textArea = document.createElement('textarea');
        textArea.value = text;
        
        // 设置样式使其不可见
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        textArea.style.top = '0';
        textArea.style.opacity = '0';
        
        document.body.appendChild(textArea);
        
        // 选择并复制文本
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            callback();
        } catch (err) {
            console.error('复制失败:', err);
        }
        
        // 清理
        document.body.removeChild(textArea);
    } catch (err) {
        console.error('复制失败:', err);
    }
}

// 获取IP信息
function fetchIPInfo(ip) {
    if (!ip) {
        $("#result").html('<div class="alert alert-danger">IP地址无效</div>');
        return;
    }

    console.log("开始获取IP信息:", ip);
    window.currentQueryIP = ip;

    // 显示加载动画
    $("#result").html(`
        <div class="loading">
            <div>
                <div class="spinner-border text-primary mb-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div>正在查询IP相关信息...</div>
            </div>
        </div>
    `);

    // 设置请求超时
    const timeout = setTimeout(() => {
        if ($("#result").find(".loading").length > 0) {
            $("#result").html('<div class="alert alert-warning">请求超时，请稍后重试</div>');
        }
    }, 10000);

    $.ajax({
        url: `/api/${ip}`,
        method: 'GET',
        timeout: 10000,
        success: function(data) {
            clearTimeout(timeout);
            if (data && !data.error) {
                displayResult(ip, data);
            } else {
                $("#result").html(`<div class="alert alert-danger">查询失败: ${data.error || '未知错误'}</div>`);
            }
        },
        error: function(xhr, status, error) {
            clearTimeout(timeout);
            console.error("IP信息获取错误:", error);
            let errorMessage = '无法连接到服务器';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            $("#result").html(`<div class="alert alert-danger">查询失败: ${errorMessage}</div>`);
        }
    });
}

// 执行IP查询
function executeIPQuery(ip) {
    if (window.timeInterval) {
        clearInterval(window.timeInterval);
    }

    $("#searchBox").slideUp(200);
    $("#ipInput").val("");
    fetchIPInfo(ip);
}

// 页面加载和事件处理
$(document).ready(function () {
    $("#ipInput").on("keypress", function (e) {
        if (e.which === 13) {
            const ip = $(this).val().trim();
            if (ip) {
                executeIPQuery(ip);
            }
        }
    });

    // 获取当前IP信息
    $.ajax({
        url: "/api/current",
        method: 'GET',
        timeout: 5000,
        success: function(data) {
            if (data && data.ip) {
                fetchIPInfo(data.ip);
            } else {
                $("#result").html('<div class="alert alert-danger">无法获取当前IP地址</div>');
            }
        },
        error: function(xhr, status, error) {
            console.error("获取当前IP错误:", error);
            let errorMessage = '无法获取当前IP地址';
            if (xhr.responseJSON && xhr.responseJSON.error) {
                errorMessage = xhr.responseJSON.error;
            }
            $("#result").html(`<div class="alert alert-danger">${errorMessage}</div>`);
        }
    });

    updateTime();

    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.type === "childList") {
                $(".card-body .info-row:first-child").css("padding-top", "0");
                $(".card-body .info-row:last-child").css("padding-bottom", "0");
            }
        });
    });

    observer.observe(document.getElementById("result"), {
        childList: true,
        subtree: true,
    });
});

// 全局函数
window.showSearchInput = function () {
    $("#searchBox").slideDown(200);
    $("#ipInput").focus();

    setTimeout(() => {
        $(document).on("click.searchbox", function (e) {
            const ip = $("#ipInput").val().trim();

            if (!$(e.target).closest("#ipInput").length && !$(e.target).closest(".fa-search").length) {
                if (ip) {
                    executeIPQuery(ip);
                } else {
                    $("#searchBox").slideUp(200);
                }
                $(document).off("click.searchbox");
            }
        });
    }, 0);
};

window.copyIP = function (ip) {
    navigator.clipboard
        .writeText(ip)
        .then(function () {
            const tooltip = $(".ip-value .copy-tooltip");
            tooltip.fadeIn(200);
            setTimeout(() => {
                tooltip.fadeOut(200);
            }, 1500);
        })
        .catch(function (err) {
            console.error("复制失败:", err);
        });
}; 