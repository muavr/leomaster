let url = '/api/masterclasses/';
let inProcess = false;

function printDateTime(stringDate) {
    let date = new Date(stringDate);
    let localTime = date.toLocaleTimeString(date, {hour: '2-digit', minute: '2-digit'});
    let localYear = date.toLocaleDateString(date, {year: 'numeric'});
    let localMonth = date.toLocaleDateString(date, {month: '2-digit'});
    let localDay = date.toLocaleDateString(date, {day: '2-digit'});
    return `${localDay}-${localMonth}-${localYear} ${localTime}`
}

function printWeekday(stringDate) {
    let date = new Date(stringDate);
    return date.toLocaleDateString(date, {weekday: 'long'});
}

function isWeekend(stringDate) {
    let date = new Date(stringDate);
    return date.getDay() === 0 || date.getDay() === 6
}

function printFullDate(stringDate) {
    // "d-m-Y H:i, l"
    let localDateTime = printDateTime(stringDate);
    let localWeekday = printWeekday(stringDate);
    return `${localDateTime}, ${localWeekday}`
}

function printComplexity(value, total) {
    let widget = '';
    let style = '';
    for (let i = 1; i <= total; ++i) {
        style = i > value ? 'style="opacity: 0.4"' : '';
        widget += `<i class="icon fa fa-paint-brush fa-fw" ${style}></i>`
    }
    return widget;
}

function financial(x) {
    return Number.parseFloat(x).toFixed(2);
}

function toTime(seconds) {
    let days = Math.trunc(seconds / 60 / 60 / 24);
    seconds = seconds - days * 60 * 60 * 24;
    let hours = Math.trunc(seconds / 60 / 60);
    seconds = seconds - hours * 60 * 60;
    let minutes = Math.trunc(seconds / 60);
    seconds = seconds - minutes * 60;
    return `${days > 0 ? days + " дней " : ""}${hours > 0 ? hours + " ч. " : ""}${minutes > 0 ? minutes + " мин. " : ""}${seconds > 0 ? seconds + " сек. " : ""}`
}

function download() {
    if (url && !inProcess) {
        $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json',
            beforeSend: function () {
                $('.loader').removeClass('hidden');
                inProcess = true;
            }
        })
        .done(function (data) {
            url = data.next;
            let content = data.results;
            console.log(content);
            if (content) {
                content.forEach(function (mc) {
                    $('.grid-container').append(`
                        <div class="grid-item">
                            <div class="card text-center rounded-0 mc-block ${mc.avail_seats ? "" : "not-available"} ${isWeekend(mc.date) ? "holiday" : ""}" style="width: 100%;">
                                <div class="card-body d-flex flex-column">
                                    <img data-toggle="modal" data-target="#mcDescription_${mc.uid}" src="/media/downloads/img/${mc.uid}.jpeg" alt="${mc.title}" class="img-thumbnail rounded-0">
                                    <h6 class="card-title">${mc.title}</h6>
                                    <div class="mc-short-description mt-auto text-left">
                                        <hr>
                                        <i class="icon fa fa-clock-o fa-fw" aria-hidden="true"></i> ${printDateTime(mc.date)}<br>
                                        <i class="icon fa fa-calendar fa-fw" aria-hidden="true"></i>${printWeekday(mc.date)}<br>
                                        <i class="icon fa fa-rub fa-fw" aria-hidden="true"></i> ${financial(mc.online_price)}<br>
                                        <i class="icon fa fa-users fa-fw" aria-hidden="true"></i> ${mc.avail_seats}
                                    </div>
                                </div>
                            </div>
                            <div class="modal fade" id="mcDescription_${mc.uid}" tabindex="-1" role="dialog" aria-labelledby="mcDescription_${mc.uid}Title" aria-hidden="true">
                                <div class="modal-dialog modal-dialog-centered" role="document">
                                    <div class="modal-content rounded-0">
                                        <div class="modal-header text-left">
                                            <h5 class="modal-title" id="mcDescription_${mc.uid}Title">${mc.title}</h5>
                                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                                <span aria-hidden="true">&times;</span>
                                            </button>
                                        </div>
                                        <div class="modal-body text-justify">
                                            <div class="clearfix">
                                                <p class="float-left">${printFullDate(mc.date)}</p>
                                                <p class="float-right">${printComplexity(mc.complexity, mc.max_complexity)}</p>
                                            </div>
                                            <p><img src="/media/downloads/img/${mc.uid}_preview.jpeg" alt="${mc.title}" class="img-thumbnail rounded-0"></p>
                                            <div class="mc-detail">
                                                <p><i class="icon fa fa-map-marker fa-fw" aria-hidden="true"></i> ${mc.location}</p>
                                                <p><i class="icon fa fa-user fa-fw"></i> ${mc.master}</p>
                                                <p><i class="icon fa fa-rub fa-fw" aria-hidden="true"></i> ${financial(mc.online_price)} / ${financial(mc.price)}</p>
                                                <p><i class="icon fa fa-users fa-fw" aria-hidden="true"></i> ${mc.avail_seats} из ${mc.total_seats}</p>
                                                <p><i class="icon fa fa-hourglass-half fa-fw"></i> ${toTime(mc.duration)}</p>
                                                <p><i class="icon fa fa-warning fa-fw" aria-hidden="true"></i> ${mc.age_restriction}</p>
                                            </div>
                                            <hr>
                                            ${mc.description}
                                        </div>
                                        <div class="modal-footer">
                                            <button type="button" class="btn btn-secondary rounded-0" data-dismiss="modal">Ладно</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`)
                })
            }

        })
        .always(function () {
            $('.loader').addClass('hidden');
            inProcess = false;
        })
    }
}

$(document).ready(function () {
    url += $('#pageGroup').data('group');
    download()
});

$(window).scroll(function () {
    if ($(window).scrollTop() + 20 >= $(document).height() - $(window).height()) {
        download()
    }
});